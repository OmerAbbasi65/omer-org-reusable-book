from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from . import models
from .database import SessionLocal, engine
import os
from dotenv import load_dotenv
from .prepare_content import get_embedding # For generating query embeddings
from .qdrant_utils import get_qdrant_client # For Qdrant client
from typing import List, Dict, Optional
import openai # Added import for OpenAI API calls

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request models
class ChatRequest(BaseModel):
    message: str
    session_id: str
    selected_text: Optional[str] = None

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable not set.")

# Initialize OpenAI-compatible client with OpenRouter
openai_client = openai.OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url=OPENROUTER_BASE_URL
)

async def generate_rag_response(user_message: str, db: Session) -> str:
    """
    Generates a RAG response by retrieving relevant chunks from Qdrant
    and using OpenAI's chat model.
    """
    if not QDRANT_COLLECTION_NAME:
        raise HTTPException(status_code=500, detail="QDRANT_COLLECTION_NAME not configured.")

    # 1. Retrieve relevant chunks
    query_embedding = get_embedding(user_message)
    qdrant_client_instance = get_qdrant_client()

    search_result = qdrant_client_instance.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_embedding,
        limit=3, # Retrieve top 3 relevant chunks
        append_payload=True,
    )
    
    context = "\n".join([hit.payload["content"] for hit in search_result])

    # 2. Construct prompt for LLM
    system_prompt = (
        "You are a helpful assistant that answers questions based on the provided book content. "
        "If you cannot find the answer in the provided context, please state that you don't know "
        "or that the information is not available in the book."
    )
    user_prompt = f"Question: {user_message}\n\nBook Content:\n{context}\n\nAnswer:"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # 3. Get response from LLM
    try:
        response = openai_client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating LLM response: {e}")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/conversations/")
def create_conversation(user_id: str, message: str, response_text: str, db: Session = Depends(get_db)): # Modified to accept response_text
    db_conversation = models.Conversation(user_id=user_id, message=message, response=response_text) # Modified
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

@app.get("/conversations/{user_id}")
def read_conversations(user_id: str, db: Session = Depends(get_db)):
    conversations = db.query(models.Conversation).filter(models.Conversation.user_id == user_id).all()
    return conversations

@app.post("/retrieve_chunks")
async def retrieve_chunks(query: str, limit: int = 3) -> List[Dict]:
    """
    Retrieves relevant document chunks from Qdrant based on the user query.
    """
    if not QDRANT_COLLECTION_NAME:
        raise HTTPException(status_code=500, detail="QDRANT_COLLECTION_NAME not configured.")

    query_embedding = get_embedding(query)
    qdrant_client_instance = get_qdrant_client()

    search_result = qdrant_client_instance.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_embedding,
        limit=limit,
        append_payload=True, # Ensure payload (original text) is returned
    )
    
    chunks = []
    for hit in search_result:
        chunks.append({
            "content": hit.payload["content"],
            "file_path": hit.payload["file_path"],
            "score": hit.score,
        })
    return chunks

@app.post("/api/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Main chat endpoint that uses RAG to answer user questions based on book content.
    """
    llm_response = await generate_rag_response(request.message, db)

    # Store conversation in DB
    conversation = models.Conversation(
        user_id=request.session_id,
        message=request.message,
        response=llm_response
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return {
        "response": llm_response,
        "session_id": request.session_id,
        "message": request.message
    }