"""Utilities for text embedding with OpenAI."""
from typing import List
from openai import OpenAI
from ..config.settings import settings

client = OpenAI(api_key=settings.openai_api_key)


async def embed_text(text: str) -> List[float]:
    """Embed a single text string using OpenAI embeddings."""
    response = client.embeddings.create(
        model=settings.embedding_model,
        input=text
    )
    return response.data[0].embedding


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed multiple text strings in batch."""
    response = client.embeddings.create(
        model=settings.embedding_model,
        input=texts
    )
    return [item.embedding for item in response.data]
