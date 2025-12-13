import os
import re
import json
import openai
from dotenv import load_dotenv
from qdrant_client.models import Distance, VectorParams
from .qdrant_utils import get_qdrant_client, recreate_qdrant_collection, upsert_vectors_to_collection

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
if not QDRANT_COLLECTION_NAME:
    raise ValueError("QDRANT_COLLECTION_NAME environment variable not set.")

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

def get_files_in_directory(directory, extensions=None):
    """Recursively gets all files in a directory with specified extensions."""
    if extensions is None:
        extensions = []
    
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_list.append(os.path.join(root, file))
    return file_list

def clean_markdown_content(content):
    """Removes Docusaurus frontmatter and performs basic cleanup."""
    # Remove YAML frontmatter (lines between ---
(.*?)
---)
    cleaned_content = re.sub(r'---\n(.*?)\n---', '', content, flags=re.DOTALL)
    
    # Remove any remaining HTML tags (e.g., from MDX)
    cleaned_content = re.sub(r'<[^>]+>', '', cleaned_content)
    
    # Replace multiple newlines with single ones
    cleaned_content = re.sub(r'\n\s*\n', '\n\n', cleaned_content)
    
    # Trim leading/trailing whitespace
    cleaned_content = cleaned_content.strip()
    return cleaned_content

def chunk_text(text, chunk_size=500, overlap=50):
    """Splits text into chunks with specified overlap."""
    if not text:
        return []

    words = text.split()
    chunks = []
    
    i = 0
    while i < len(words):
        current_chunk_words = []
        current_length = 0
        
        # Add overlap from the previous chunk
        if i > 0 and overlap > 0 and len(chunks) > 0: # Ensure chunks is not empty
            # Take last 'overlap' words from the previous chunk's words
            prev_chunk_words = chunks[-1].split()
            overlap_words = prev_chunk_words[-min(overlap, len(prev_chunk_words)):]
            current_chunk_words.extend(overlap_words)
            current_length = sum(len(w) for w in current_chunk_words) + len(current_chunk_words) - 1 if current_chunk_words else 0

        # Fill the rest of the chunk
        j = i
        while j < len(words) and current_length + len(words[j]) + 1 <= chunk_size:
            current_chunk_words.append(words[j])
            current_length += len(words[j]) + 1
            j += 1
        
        if current_chunk_words:
            chunks.append(" ".join(current_chunk_words))
        
        # Move the index forward, ensuring progress
        if j == i: # If no new words were added to the chunk, advance by 1 to avoid infinite loop
            i += 1
        else:
            i = j
            
    return chunks

def get_embedding(text):
    """Generates an embedding for the given text using OpenAI's model."""
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-ada-002" # Or another suitable embedding model
    )
    return response.data[0].embedding

def process_book_content(book_root_dir):
    """
    Processes all markdown/mdx files in the book directory,
    cleans them, chunks them, generates embeddings, and upserts to Qdrant.
    """
    docs_dir = os.path.join(book_root_dir, "docs")
    blog_dir = os.path.join(book_root_dir, "blog")

    markdown_files = get_files_in_directory(docs_dir, extensions=[".md", ".mdx"])
    markdown_files.extend(get_files_in_directory(blog_dir, extensions=[".md", ".mdx"]))

    all_vectors = []
    all_payloads = []
    
    qdrant_client_instance = get_qdrant_client()
    
    # Recreate collection - assuming text-embedding-ada-002 produces 1536-dim vectors
    # This ensures a clean slate each time content is processed.
    recreate_qdrant_collection(qdrant_client_instance, vector_size=1536, collection_name=QDRANT_COLLECTION_NAME)

    for file_path in markdown_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        cleaned_content = clean_markdown_content(content)
        chunks = chunk_text(cleaned_content)

        for i, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            all_vectors.append(embedding)
            all_payloads.append({
                "file_path": file_path,
                "chunk_id": i,
                "content": chunk,
            })
    
    if all_vectors:
        upsert_vectors_to_collection(qdrant_client_instance, all_vectors, all_payloads, collection_name=QDRANT_COLLECTION_NAME)
    
    print(f"Processed {len(markdown_files)} files. Generated and upserted {len(all_vectors)} embeddings.")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    book_root_dir = os.path.join(current_dir, "../../reusable-book")
    
    if not os.path.exists(book_root_dir):
        print(f"Error: Book root directory not found at {book_root_dir}")
    else:
        process_book_content(book_root_dir)
