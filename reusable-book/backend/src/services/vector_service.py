"""Vector search service using Qdrant."""
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, SearchParams
from ..config.settings import settings
from ..utils.embeddings import embed_text


class VectorService:
    """Service for vector similarity search operations."""

    def __init__(self):
        """Initialize Qdrant client."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key
        )
        self.collection_name = settings.qdrant_collection_name

    async def search(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for similar text chunks in the vector store."""
        if top_k is None:
            top_k = settings.top_k_retrieval

        query_vector = await embed_text(query)

        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            search_params=SearchParams(exact=False)
        )

        results = []
        for point in search_result:
            results.append({
                "chunk_id": point.id,
                "text": point.payload.get("text", ""),
                "chapter": point.payload.get("chapter", ""),
                "section": point.payload.get("section", ""),
                "page_url": point.payload.get("page_url", ""),
                "score": point.score
            })

        return results


vector_service = VectorService()
