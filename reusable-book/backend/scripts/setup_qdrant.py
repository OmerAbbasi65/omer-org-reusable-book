"""Setup Qdrant collection for book content"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from src.config import settings

def setup_qdrant():
    """Create Qdrant collection for book content"""
    print(f"Connecting to Qdrant at {settings.qdrant_url}...")

    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key
    )

    # Check if collection exists
    collections = client.get_collections().collections
    collection_names = [c.name for c in collections]

    if settings.qdrant_collection in collection_names:
        print(f"⚠️  Collection '{settings.qdrant_collection}' already exists")
        response = input("Delete and recreate? (y/N): ")
        if response.lower() == 'y':
            client.delete_collection(settings.qdrant_collection)
            print(f"✓ Deleted existing collection")
        else:
            print("Keeping existing collection")
            return

    # Create collection
    client.create_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=VectorParams(
            size=1536,  # text-embedding-3-small dimensions
            distance=Distance.COSINE
        )
    )

    print(f"✅ Created Qdrant collection '{settings.qdrant_collection}'")
    print(f"   - Vector size: 1536 (text-embedding-3-small)")
    print(f"   - Distance metric: COSINE")

if __name__ == "__main__":
    setup_qdrant()
