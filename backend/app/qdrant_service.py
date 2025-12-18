from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import uuid
from .config import settings

class QdrantService:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.qdrant_collection_name
        # Use HuggingFace sentence-transformers (free, runs locally)
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        # all-MiniLM-L6-v2 produces 384-dimensional embeddings
        self.embedding_dimension = 384

        # Initialize collection if it doesn't exist
        self._init_collection()

    def _init_collection(self):
        """Initialize Qdrant collection if it doesn't exist"""
        try:
            self.client.get_collection(self.collection_name)
            print(f"Collection '{self.collection_name}' already exists")
        except Exception:
            print(f"Creating collection '{self.collection_name}'")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.embedding_dimension,
                    distance=Distance.COSINE
                )
            )

    def create_embedding(self, text: str) -> List[float]:
        """Create embedding vector for text using HuggingFace sentence-transformers"""
        embedding = self.embedding_model.encode(text)
        return embedding.tolist()

    def add_document(self, doc_id: str, title: str, content: str, metadata: Dict[str, Any]) -> str:
        """Add a document to Qdrant"""
        # Create embedding
        embedding = self.create_embedding(content)

        # Generate unique ID
        vector_id = str(uuid.uuid4())

        # Create point
        point = PointStruct(
            id=vector_id,
            vector=embedding,
            payload={
                "doc_id": doc_id,
                "title": title,
                "content": content,
                **metadata
            }
        )

        # Upsert to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        return vector_id

    def add_documents_batch(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Add multiple documents in batch"""
        points = []
        vector_ids = []

        for doc in documents:
            # Create embedding
            embedding = self.create_embedding(doc["content"])

            # Generate unique ID
            vector_id = str(uuid.uuid4())
            vector_ids.append(vector_id)

            # Create point
            point = PointStruct(
                id=vector_id,
                vector=embedding,
                payload={
                    "doc_id": doc.get("doc_id", str(uuid.uuid4())),
                    "title": doc["title"],
                    "content": doc["content"],
                    **doc.get("metadata", {})
                }
            )
            points.append(point)

        # Batch upsert
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

        return vector_ids

    def search(self, query: str, top_k: int = 5, filter_dict: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        # Create query embedding
        query_embedding = self.create_embedding(query)

        # Build filter if provided
        search_filter = None
        if filter_dict:
            conditions = []
            for key, value in filter_dict.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            if conditions:
                search_filter = Filter(must=conditions)

        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=search_filter
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "score": result.score,
                "title": result.payload.get("title", ""),
                "content": result.payload.get("content", ""),
                "chapter_id": result.payload.get("chapter_id", ""),
                "metadata": {k: v for k, v in result.payload.items()
                            if k not in ["title", "content", "chapter_id", "doc_id"]}
            })

        return formatted_results

    def delete_document(self, vector_id: str):
        """Delete a document from Qdrant"""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(
                points=[vector_id]
            )
        )

    def delete_by_chapter(self, chapter_id: str):
        """Delete all documents for a specific chapter"""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(
                filter=Filter(
                    must=[
                        FieldCondition(
                            key="chapter_id",
                            match=MatchValue(value=chapter_id)
                        )
                    ]
                )
            )
        )

# Singleton instance
qdrant_service = QdrantService()
