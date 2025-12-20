import os
import re
import json
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

# Initialize the embedding model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
embedding_model = SentenceTransformer(EMBEDDING_MODEL)

def get_embedding(text):
    """
    Generates an embedding vector for the given text using HuggingFace SentenceTransformer.
    Returns a list of floats representing the embedding.
    """
    embedding = embedding_model.encode(text)
    return embedding.tolist()

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
    # Remove YAML frontmatter (lines between ---\n(.*?)\n---)
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
        if i > 0 and overlap > 0:
            start_overlap_idx = max(0, i - overlap)
            current_chunk_words.extend(words[start_overlap_idx:i])
            current_length = sum(len(w) for w in current_chunk_words) + len(current_chunk_words) - 1 if current_chunk_words else 0

        # Fill the rest of the chunk
        j = i
        while j < len(words) and current_length + len(words[j]) + 1 <= chunk_size:
            current_chunk_words.append(words[j])
            current_length += len(words[j]) + 1
            j += 1
        
        if current_chunk_words:
            chunks.append(" ".join(current_chunk_words))
        
        # Move the index forward, accounting for overlap
        if j == i: # If no new words were added to the chunk, advance by 1 to avoid infinite loop
            i += 1
        else:
            i = j
            
    return chunks

def process_book_content(book_root_dir, output_file="processed_chunks.json"):
    """
    Processes all markdown/mdx files in the book directory,
    cleans them, chunks them, and saves to a JSON file.
    """
    docs_dir = os.path.join(book_root_dir, "docs")
    blog_dir = os.path.join(book_root_dir, "blog")

    markdown_files = get_files_in_directory(docs_dir, extensions=[".md", ".mdx"])
    markdown_files.extend(get_files_in_directory(blog_dir, extensions=[".md", ".mdx"]))

    all_chunks_data = []

    for file_path in markdown_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        cleaned_content = clean_markdown_content(content)
        chunks = chunk_text(cleaned_content)

        for i, chunk in enumerate(chunks):
            all_chunks_data.append({
                "file_path": file_path,
                "chunk_id": i,
                "content": chunk,
            })
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks_data, f, indent=2)
    
    print(f"Processed {len(markdown_files)} files into {len(all_chunks_data)} chunks.")
    print(f"Chunks saved to {output_file}")

if __name__ == "__main__":
    # Assuming the script is run from the `backend/chatbot` directory
    # and `reusable-book` is in the parent directory.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    book_root_dir = os.path.join(current_dir, "../../reusable-book")
    
    if not os.path.exists(book_root_dir):
        print(f"Error: Book root directory not found at {book_root_dir}")
    else:
        process_book_content(book_root_dir)
