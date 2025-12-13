import os
import openai
from qdrant_client import models, QdrantClient
from langchain.text_splitter import RecursiveCharacterTextSplitter
# This would be a more robust loader in a real scenario
def load_book_content(docs_path):
    all_text = ""
    for filename in os.listdir(docs_path):
        if filename.endswith(".md"):
            with open(os.path.join(docs_path, filename), "r", encoding="utf-8") as f:
                all_text += f.read()
    return all_text

def get_openai_embeddings(text_chunks):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text_chunks
    )
    return [item['embedding'] for item in response['data']]

def ingest_content(docs_path, qdrant_client: QdrantClient, collection_name="book_content"):
    # 1. Load content
    book_text = load_book_content(docs_path)

    # 2. Split content into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_text(book_text)

    # 3. Get embeddings
    embeddings = get_openai_embeddings(chunks)

    # 4. Upsert into Qdrant
    qdrant_client.upsert(
        collection_name=collection_name,
        points=models.Batch(
            ids=[i for i in range(len(chunks))],
            vectors=embeddings,
            payloads=[{"text": chunk} for chunk in chunks]
        )
    )
    print(f"Successfully ingested {len(chunks)} chunks into Qdrant.")

if __name__ == '__main__':
    from qdrant_utils import qdrant_client
    # This assumes the script is run from the 'backend/chatbot' directory
    book_docs_path = "../../reusable-book/docs"
    
    # Create collection if it doesn't exist
    try:
        qdrant_client.recreate_collection(
            collection_name="book_content",
            vectors_config=models.VectorParams(size=1536, distance=models.Distance.COSINE),
        )
        print("Created Qdrant collection 'book_content'")
    except Exception as e:
        print(f"Collection already exists or another error occurred: {e}")

    ingest_content(book_docs_path, qdrant_client)
