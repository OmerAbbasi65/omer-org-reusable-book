import qdrant_client
from qdrant_client.models import Distance, VectorParams, PointStruct
import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME") # New: collection name from env

def get_qdrant_client():
    """Initializes and returns a Qdrant client."""
    client = qdrant_client.QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
    )
    return client

def recreate_qdrant_collection(client: qdrant_client.QdrantClient, vector_size: int, collection_name: str = QDRANT_COLLECTION_NAME):
    """
    Recreates a Qdrant collection with the given name and vector size.
    If the collection already exists, it will be deleted and recreated.
    """
    if client.collection_exists(collection_name=collection_name):
        client.delete_collection(collection_name=collection_name)
        print(f"Collection '{collection_name}' deleted.")

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )
    print(f"Collection '{collection_name}' created with vector size {vector_size}.")

def upsert_vectors_to_collection(client: qdrant_client.QdrantClient, vectors: list, payloads: list, collection_name: str = QDRANT_COLLECTION_NAME):
    """
    Upserts vectors and their corresponding payloads to a Qdrant collection.
    
    Args:
        client: Qdrant client instance.
        vectors: List of embedding vectors.
        payloads: List of dictionaries, where each dictionary is the metadata for a vector.
        collection_name: The name of the collection to upsert into.
    """
    points = []
    for i, (vector, payload) in enumerate(zip(vectors, payloads)):
        points.append(
            PointStruct(
                id=i, # Qdrant will assign a UUID if not provided, but explicit ID is better for consistency
                vector=vector,
                payload=payload,
            )
        )
    
    # Batch upsert points
    client.upsert(
        collection_name=collection_name,
        wait=True,
        points=points
    )
    print(f"Upserted {len(points)} points to collection '{collection_name}'.")

# Example usage (for testing purposes, will not be executed directly by the agent)
if __name__ == "__main__":
    # Ensure environment variables are set for testing
    os.environ["QDRANT_URL"] = "http://localhost:6333" # Or your cloud instance
    os.environ["QDRANT_API_KEY"] = "your_api_key_if_any"
    os.environ["QDRANT_COLLECTION_NAME"] = "test_collection"

    qdrant_client_instance = get_qdrant_client()
    
    # Recreate collection (e.g., for an embedding model that produces 1536-dim vectors)
    recreate_qdrant_collection(qdrant_client_instance, vector_size=1536)

    # Dummy data
    dummy_vectors = [[0.1]*1536, [0.2]*1536, [0.3]*1536]
    dummy_payloads = [
        {"content": "This is a test document 1."},
        {"content": "This is another test document 2."},
        {"content": "And a third one for good measure 3."}
    ]
    
    upsert_vectors_to_collection(qdrant_client_instance, dummy_vectors, dummy_payloads)
    
    # You can also add search functionality for testing here
    search_result = qdrant_client_instance.search(
        collection_name="test_collection",
        query_vector=[0.15]*1536,
        limit=1
    )
    print("Search Result:", search_result)
