"""
Document Ingestion Script for Physical AI & Humanoid Robotics Textbook

This script:
1. Reads all markdown files from the docs directory
2. Chunks them appropriately
3. Creates embeddings
4. Stores them in Qdrant and PostgreSQL

Usage:
    python ingest_documents.py
"""

import os
import sys
import requests
import re
from pathlib import Path
from typing import List, Dict
import frontmatter

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DOCS_DIR = Path(__file__).parent.parent / "reusable-book" / "docs"
API_URL = "http://localhost:8000/api/documents/ingest"

def read_markdown_file(file_path: Path) -> Dict:
    """Read markdown file and extract frontmatter + content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        return {
            "frontmatter": post.metadata,
            "content": post.content,
            "file_path": str(file_path)
        }
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def chunk_content(content: str, max_chunk_size: int = 1000) -> List[str]:
    """
    Chunk content into smaller pieces for better retrieval.
    Splits on headers and paragraphs.
    """
    # Split by headers (##, ###, etc.)
    sections = re.split(r'(#+\s+.+)', content)

    chunks = []
    current_chunk = ""
    current_header = ""

    for section in sections:
        # Check if it's a header
        if re.match(r'#+\s+', section):
            # Save previous chunk if it exists
            if current_chunk.strip():
                chunks.append(current_header + "\n\n" + current_chunk)
            current_header = section
            current_chunk = ""
        else:
            # Add to current chunk
            current_chunk += section

            # If chunk is getting too large, split it
            if len(current_chunk) > max_chunk_size:
                # Split by paragraphs
                paragraphs = current_chunk.split('\n\n')
                temp_chunk = ""

                for para in paragraphs:
                    if len(temp_chunk) + len(para) > max_chunk_size and temp_chunk:
                        chunks.append(current_header + "\n\n" + temp_chunk)
                        temp_chunk = para
                    else:
                        temp_chunk += "\n\n" + para if temp_chunk else para

                current_chunk = temp_chunk

    # Add final chunk
    if current_chunk.strip():
        chunks.append(current_header + "\n\n" + current_chunk)

    return [chunk.strip() for chunk in chunks if chunk.strip()]

def process_document(file_path: Path) -> List[Dict]:
    """Process a markdown document into chunks ready for ingestion"""
    doc = read_markdown_file(file_path)
    if not doc:
        return []

    frontmatter = doc["frontmatter"]
    content = doc["content"]

    # Get chapter info from frontmatter
    chapter_id = frontmatter.get("id", file_path.stem)
    title = frontmatter.get("title", file_path.stem.replace("-", " ").title())

    # Chunk the content
    chunks = chunk_content(content)

    # Create document chunks for API
    document_chunks = []
    for i, chunk in enumerate(chunks):
        document_chunks.append({
            "title": f"{title} - Part {i+1}",
            "content": chunk,
            "chapter_id": chapter_id,
            "metadata": {
                "file_path": str(file_path),
                "chunk_index": i,
                "total_chunks": len(chunks),
                "sidebar_position": frontmatter.get("sidebar_position"),
            }
        })

    return document_chunks

def ingest_documents():
    """Main ingestion function"""
    print("🚀 Starting document ingestion...")
    print(f"📁 Reading from: {DOCS_DIR}")

    # Find all markdown files
    md_files = list(DOCS_DIR.glob("*.md"))
    md_files += list(DOCS_DIR.glob("*.mdx"))

    # Filter out tutorial files if needed
    md_files = [f for f in md_files if "tutorial" not in str(f)]

    print(f"📄 Found {len(md_files)} markdown files")

    all_chunks = []

    # Process each file
    for md_file in md_files:
        print(f"Processing: {md_file.name}")
        chunks = process_document(md_file)
        all_chunks.extend(chunks)
        print(f"  ✓ Created {len(chunks)} chunks")

    print(f"\n📦 Total chunks to ingest: {len(all_chunks)}")

    # Send to API
    try:
        print(f"📤 Sending to API: {API_URL}")
        response = requests.post(
            API_URL,
            json={"documents": all_chunks},
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! {result.get('message')}")
            print(f"📚 Ingested documents: {', '.join(result.get('documents', []))}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API")
        print("Make sure the FastAPI server is running:")
        print("  cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("=" * 60)
    print("Physical AI & Humanoid Robotics - Document Ingestion")
    print("=" * 60)
    ingest_documents()
    print("\n" + "=" * 60)
    print("✨ Ingestion complete!")
    print("=" * 60)
