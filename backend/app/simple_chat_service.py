from openai import OpenAI
from typing import List, Dict, Any, Optional
from .config import settings

class SimpleChatService:
    def __init__(self):
        # Use OpenRouter with OpenAI-compatible API
        self.client = OpenAI(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
        )
        # Use current_model which switches between Claude and Cohere
        self.model = settings.current_model
        self.max_tokens = 1024
        self.active_model_type = settings.active_model

    def generate_response(
        self,
        query: str,
        selected_text: Optional[str] = None,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response using OpenRouter (simple chat, no RAG).

        Args:
            query: User's question
            selected_text: Text selected by user (for context-specific questions)
            conversation_history: Previous messages in conversation

        Returns:
            Dictionary with response
        """
        # Build messages for chat
        messages = self._build_messages(query, selected_text, conversation_history)

        # Generate response using OpenRouter
        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "system", "content": self._get_system_prompt()}] + messages
        )

        answer = response.choices[0].message.content

        return {
            "response": answer,
            "sources": [],
            "confidence": 1.0
        }

    def _get_system_prompt(self) -> str:
        """Get system prompt optimized for the active model"""
        base_prompt = """You are an expert AI tutor for Physical AI and Humanoid Robotics.
Your role is to help students understand concepts about robotics, ROS 2, simulation, and AI.

Guidelines:
1. Provide clear, accurate answers based on your knowledge
2. Use examples and analogies to clarify complex concepts
3. Be concise but thorough
4. Use technical terms correctly and define them when necessary
5. If you're not sure about something, say so honestly
6. Encourage deeper understanding by asking follow-up questions when appropriate

Topics you can help with:
- ROS 2 (Robot Operating System)
- Gazebo and Unity simulation
- NVIDIA Isaac platform
- Vision-Language-Action (VLA) models
- Humanoid robotics
- Physical AI concepts
"""

        # Add model-specific optimizations
        if self.active_model_type.lower() == "cohere":
            base_prompt += "\nYou are powered by Cohere's Command R+ model, optimized for retrieval-augmented generation and educational content."
        else:
            base_prompt += "\nYou are powered by Claude 3.5 Sonnet, Anthropic's advanced AI assistant."

        return base_prompt

    def _build_messages(
        self,
        query: str,
        selected_text: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Dict[str, str]]:
        """Build message list for Claude API"""
        messages = []

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history[-5:]:  # Last 5 messages
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # Build current query
        if selected_text:
            user_message = f"""I selected this text:
```
{selected_text}
```

Question: {query}"""
        else:
            user_message = query

        messages.append({"role": "user", "content": user_message})

        return messages

# Lazy singleton instance
_simple_chat_service_instance = None

def get_simple_chat_service():
    global _simple_chat_service_instance
    if _simple_chat_service_instance is None:
        _simple_chat_service_instance = SimpleChatService()
    return _simple_chat_service_instance

# For backward compatibility
simple_chat_service = type('LazyService', (), {
    '__getattr__': lambda self, name: getattr(get_simple_chat_service(), name)
})()
