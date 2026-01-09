from typing import Dict, Any, Optional
from langchain_ollama import OllamaEmbeddings
from datetime import datetime
import uuid
import logging

from .rag_utils import load_rag_db, save_rag_db, chunk_text

logger = logging.getLogger("mcp_server")

# Initialize embeddings model
embeddings_model = OllamaEmbeddings(model="bge-large")


def rag_add(text: str, source: Optional[str] = None, chunk_size: int = 500) -> Dict[str, Any]:
    """
    Add text to the RAG system with embeddings.

    Args:
        text: The text content to add
        source: Optional source identifier
        chunk_size: Size of text chunks (default: 500 words)

    Returns:
        Dictionary with added document info
    """
    try:
        logger.info(f"📝 Adding text to RAG (length: {len(text)})")

        # Load existing database
        db = load_rag_db()

        # Split text into chunks
        chunks = chunk_text(text, chunk_size=chunk_size)
        logger.info(f"📦 Split into {len(chunks)} chunks")

        # Generate embeddings for all chunks
        chunk_embeddings = embeddings_model.embed_documents(chunks)

        added_docs = []

        # Store each chunk with its embedding
        for idx, (chunk, embedding) in enumerate(zip(chunks, chunk_embeddings)):
            doc_id = str(uuid.uuid4())

            doc = {
                "id": doc_id,
                "text": chunk,
                "embedding": embedding,
                "metadata": {
                    "source": source or "unknown",
                    "chunk_index": idx,
                    "timestamp": datetime.now().isoformat(),
                    "chunk_count": len(chunks)
                }
            }

            db.append(doc)
            added_docs.append({
                "id": doc_id,
                "chunk_index": idx,
                "text_preview": chunk[:100] + "..." if len(chunk) > 100 else chunk
            })

        # Save updated database
        save_rag_db(db)

        logger.info(f"✅ Added {len(chunks)} chunks to RAG")

        return {
            "success": True,
            "chunks_added": len(chunks),
            "documents": added_docs,
            "source": source or "unknown"
        }

    except Exception as e:
        logger.error(f"❌ Error adding to RAG: {e}")
        return {
            "success": False,
            "error": str(e)
        }