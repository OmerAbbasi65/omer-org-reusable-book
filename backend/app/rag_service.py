from openai import OpenAI
from typing import List, Dict, Any, Optional
from .qdrant_service import qdrant_service
from .config import settings

class RAGService:
    def __init__(self):
        # Use OpenRouter with OpenAI-compatible API
        self.client = OpenAI(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
        )
        # Use current_model which switches between Claude and Cohere
        self.model = settings.current_model
        self.active_model_type = settings.active_model
        self.max_context_chars = 24000  # Approximate character limit for context

    def count_chars(self, text: str) -> int:
        """Count characters in text (simple approximation for context limits)"""
        return len(text)

    def generate_response(
        self,
        query: str,
        selected_text: Optional[str] = None,
        chapter_id: Optional[str] = None,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using RAG (Retrieval-Augmented Generation).

        Args:
            query: User's question
            selected_text: Text selected by user (for context-specific questions)
            chapter_id: Filter results to specific chapter
            conversation_history: Previous messages in conversation

        Returns:
            Dictionary with response, sources, and confidence
        """
        # If user selected text, use that as primary context
        if selected_text:
            context = selected_text
            sources = [{"type": "selected_text", "content": selected_text[:200] + "..."}]
        else:
            # Search for relevant content
            filter_dict = {"chapter_id": chapter_id} if chapter_id else None
            search_results = qdrant_service.search(
                query=query,
                top_k=5,
                filter_dict=filter_dict
            )

            # Build context from search results
            context = self._build_context(search_results)
            sources = [
                {
                    "title": result["title"],
                    "chapter_id": result["chapter_id"],
                    "score": result["score"],
                    "content": result["content"][:200] + "..."
                }
                for result in search_results
            ]

        # Build messages for ChatCompletion
        messages = self._build_messages(query, context, conversation_history)

        # Generate response
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        answer = response.choices[0].message.content

        # Calculate confidence based on relevance scores
        confidence = self._calculate_confidence(search_results if not selected_text else [])

        return {
            "response": answer,
            "sources": sources,
            "confidence": confidence
        }

    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Build context from search results, respecting character limits"""
        context_parts = []
        total_chars = 0

        for result in search_results:
            content = f"**{result['title']}**\n{result['content']}\n\n"
            chars = self.count_chars(content)

            if total_chars + chars > self.max_context_chars:
                break

            context_parts.append(content)
            total_chars += chars

        return "\n".join(context_parts)

    def _build_messages(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """Build message list for ChatCompletion API"""
        system_prompt = """You are an expert AI tutor for Physical AI and Humanoid Robotics.
Your role is to help students understand concepts from the textbook.

Guidelines:
1. Provide clear, accurate answers based on the given context
2. If the context doesn't contain the answer, say so honestly
3. Use examples and analogies to clarify complex concepts
4. Encourage deeper understanding by asking follow-up questions when appropriate
5. Be concise but thorough
6. Use technical terms correctly and define them when necessary
7. Reference specific sections or chapters when relevant

When answering:
- Start with a direct answer
- Provide supporting details from the context
- Include code examples if relevant
- Suggest related topics to explore
"""

        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                messages.append(msg)

        # Add current query with context
        user_message = f"""Context from the textbook:
```
{context}
```

Question: {query}
"""
        messages.append({"role": "user", "content": user_message})

        return messages

    def _calculate_confidence(self, search_results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on search result relevance"""
        if not search_results:
            return 1.0  # Full confidence for selected text

        # Use top result's score as confidence
        top_score = search_results[0]["score"] if search_results else 0.0

        # Normalize to 0-1 range (cosine similarity is already 0-1)
        return min(max(top_score, 0.0), 1.0)

    def summarize_chapter(self, chapter_id: str) -> str:
        """Generate a summary of a chapter"""
        # Search for chapter content
        results = qdrant_service.search(
            query=f"summary of chapter {chapter_id}",
            top_k=10,
            filter_dict={"chapter_id": chapter_id}
        )

        if not results:
            return "No content found for this chapter."

        # Combine chapter content
        chapter_content = "\n\n".join([r["content"] for r in results])

        # Limit content length (approximate 20000 chars)
        if self.count_chars(chapter_content) > 20000:
            chapter_content = chapter_content[:20000]

        # Generate summary
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at summarizing technical textbook chapters. Create a concise, well-structured summary."
                },
                {
                    "role": "user",
                    "content": f"Please summarize this chapter:\n\n{chapter_content}"
                }
            ],
            temperature=0.5,
            max_tokens=1500
        )

        return response.choices[0].message.content

# Lazy singleton instance
_rag_service_instance = None

def get_rag_service():
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = RAGService()
    return _rag_service_instance

# For backward compatibility
rag_service = type('LazyService', (), {
    '__getattr__': lambda self, name: getattr(get_rag_service(), name)
})()
