"""Ingest book content into Qdrant for RAG"""
import sys
from pathlib import Path
import uuid

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.config import settings
from src.utils import get_embeddings_batch

def ingest_book():
    """Ingest all book content from docs/ directory"""
    print("Starting book content ingestion...")

    # Initialize Qdrant client
    client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key
    )

    # Text splitter for chunking
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,  # ~500 tokens * 4 chars/token
        chunk_overlap=200,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
        length_function=len
    )

    # Find docs directory (go up from backend to repo root)
    repo_root = Path(__file__).parent.parent.parent
    docs_path = repo_root / "docs"

    if not docs_path.exists():
        print(f"❌ Error: docs/ directory not found at {docs_path}")
        return

    print(f"Reading from: {docs_path}")

    # Collect all chunks
    chunks = []
    for md_file in docs_path.rglob("*.md"):
        # Skip node_modules and other non-content directories
        if "node_modules" in str(md_file) or ".docusaurus" in str(md_file):
            continue

        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️  Skipping {md_file}: {e}")
            continue

        # Split into chunks
        file_chunks = splitter.split_text(content)

        # Extract metadata
        relative_path = md_file.relative_to(docs_path)
        chapter = str(relative_path.parts[0]) if len(relative_path.parts) > 0 else "Unknown"

        for i, chunk_text in enumerate(file_chunks):
            chunks.append({
                "text": chunk_text,
                "chapter": chapter,
                "section": md_file.stem,
                "page_url": f"/docs/{relative_path.with_suffix('')}",
                "chunk_index": i,
                "file": str(relative_path)
            })

    print(f"✓ Split book into {len(chunks)} chunks from {len(list(docs_path.rglob('*.md')))} files")

    if not chunks:
        print("❌ No content found to ingest")
        return

    # Embed and upload chunks in batches
    points = []
    batch_size = 100

    print("Embedding chunks...")
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        texts = [c["text"] for c in batch]

        # Get embeddings
        try:
            embeddings = get_embeddings_batch(texts)
        except Exception as e:
            print(f"❌ Error getting embeddings: {e}")
            continue

        # Create points
        for j, embedding in enumerate(embeddings):
            chunk = batch[j]
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "text": chunk["text"],
                    "chapter": chunk["chapter"],
                    "section": chunk["section"],
                    "page_url": chunk["page_url"],
                    "chunk_index": chunk["chunk_index"],
                    "file": chunk["file"]
                }
            ))

        print(f"  Processed {min(i+batch_size, len(chunks))}/{len(chunks)} chunks")

    # Upload to Qdrant
    print(f"Uploading {len(points)} points to Qdrant...")
    client.upsert(
        collection_name=settings.qdrant_collection,
        points=points
    )

    print(f"\n✅ Successfully ingested {len(points)} chunks into Qdrant!")
    print(f"   Collection: {settings.qdrant_collection}")
    print(f"   Total chunks: {len(points)}")

if __name__ == "__main__":
    ingest_book()
