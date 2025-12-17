"""Chatbot service using OpenAI for conversation management."""
from typing import Optional, Dict, Any, List
from openai import OpenAI
from ..config.settings import settings
from .rag_service import rag_service


class ChatbotService:
    """Service for managing chatbot conversations with RAG."""

    def __init__(self):
        """Initialize OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.chat_model
        self.system_prompt = """You are a helpful assistant for the Physical AI & Humanoid Robotics book.
Your primary role is to answer questions about the book's content, using the provided book excerpts.

When answering:
1. Prioritize information from the provided book content
2. If the book content doesn't contain the answer, use your general knowledge about Physical AI and Humanoid Robotics
3. Clarify when you're using general knowledge vs. book content
4. Be concise but thorough
5. If asked for simpler explanations, break down complex concepts into accessible language
6. When asked about relationships between topics, reference specific chapters/sections when possible
7. For homework help, explain concepts but don't provide direct answers

Always be helpful, accurate, and educational."""

    async def generate_response(
        self,
        message: str,
        selected_text: Optional[str] = None,
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """Generate a chatbot response using RAG."""
        rag_context = await rag_service.retrieve_context(message, selected_text)

        messages = [{"role": "system", "content": self.system_prompt}]

        if conversation_history:
            messages.extend(conversation_history)

        user_content = f"""{rag_context['formatted_context']}

User Question: {message}"""

        messages.append({"role": "user", "content": user_content})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )

            assistant_message = response.choices[0].message.content

            return {
                "response": assistant_message,
                "retrieved_chunks": rag_context["chunks"],
                "has_book_content": rag_context["has_relevant_content"],
                "model": self.model
            }
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")


chatbot_service = ChatbotService()
