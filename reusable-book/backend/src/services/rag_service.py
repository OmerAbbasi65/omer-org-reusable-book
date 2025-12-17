"""RAG (Retrieval-Augmented Generation) service."""
from typing import List, Dict, Any, Optional
from .vector_service import vector_service


class RAGService:
    """Service for retrieving relevant context for RAG."""

    async def retrieve_context(
        self,
        query: str,
        selected_text: Optional[str] = None,
        top_k: int = None
    ) -> Dict[str, Any]:
        """Retrieve relevant book content for a user query."""
        chunks = await vector_service.search(query, top_k=top_k)

        context_parts = []

        if selected_text:
            context_parts.append(f"Selected Text:\n{selected_text}\n")

        if chunks:
            context_parts.append("Relevant Book Content:")
            for idx, chunk in enumerate(chunks, 1):
                chapter = chunk.get("chapter", "Unknown")
                section = chunk.get("section", "")
                text = chunk.get("text", "")
                context_parts.append(
                    f"\n[{idx}] From {chapter}" +
                    (f" - {section}" if section else "") +
                    f":\n{text}"
                )

        formatted_context = "\n".join(context_parts)

        return {
            "chunks": chunks,
            "formatted_context": formatted_context,
            "has_relevant_content": len(chunks) > 0
        }


rag_service = RAGService()
