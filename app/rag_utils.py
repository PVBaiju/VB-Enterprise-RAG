"""
RAG utilities for document search and question answering using Google Gemini API
Uses local embeddings (no Databricks needed)
"""

# Suppress PyTorch/Streamlit compatibility warning
import warnings
warnings.filterwarnings("ignore")

import os
import io
import uuid
import sys
from datetime import datetime
from typing import List, Tuple, Dict, Any
import google.generativeai as genai
import pypdf
from docx import Document
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Logging setup - write to stderr so it appears in terminal
def debug_log(msg: str):
    """Print debug message to stderr (visible in terminal and logs)"""
    print(f"[DEBUG] {msg}", file=sys.stderr, flush=True)

def error_log(msg: str):
    """Print error message to stderr"""
    print(f"[ERROR] {msg}", file=sys.stderr, flush=True)

# Environment variables
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GOOGLE_MODEL_NAME = os.environ.get("GOOGLE_MODEL_NAME", "gemini-2.5-flash")  # Free tier model

# Configuration constants
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 200
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # Free, fast embedding model

# In-memory document store
DOCUMENT_STORE = {
    "documents": [],  # List of chunks with metadata
    "embeddings": [],  # Embeddings for each chunk
}


def get_llm_client():
    """Get Google Gemini AI client"""
    genai.configure(api_key=GOOGLE_API_KEY)
    return genai.GenerativeModel(GOOGLE_MODEL_NAME)


def get_embedding_model():
    """Get embedding model for generating embeddings"""
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


def extract_pdf_text(file_bytes: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
    except Exception as e:
        raise ValueError(f"Error extracting PDF: {str(e)}")


def extract_docx_text(file_bytes: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        docx_file = io.BytesIO(file_bytes)
        doc = Document(docx_file)
        return "\n".join([p.text for p in doc.paragraphs]).strip()
    except Exception as e:
        raise ValueError(f"Error extracting DOCX: {str(e)}")


def extract_txt_text(file_bytes: bytes) -> str:
    """Extract text from TXT file"""
    try:
        return file_bytes.decode("utf-8", errors="ignore").strip()
    except Exception as e:
        raise ValueError(f"Error extracting TXT: {str(e)}")


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract text from file based on extension"""
    filename_lower = filename.lower()
    
    if filename_lower.endswith(".pdf"):
        return extract_pdf_text(file_bytes)
    elif filename_lower.endswith(".docx"):
        return extract_docx_text(file_bytes)
    elif filename_lower.endswith(".txt"):
        return extract_txt_text(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {filename}")


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks"""
    text = " ".join((text or "").split())
    start = 0
    chunks = []
    
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    
    return chunks


def retrieve_context(question: str, top_k: int = 4) -> Tuple[List[str], List[Dict[str, Any]]]:
    """Retrieve relevant context using local embeddings"""
    try:
        debug_log(f"retrieve_context called with question: '{question[:50]}...'")
        debug_log(f"Document store has {len(DOCUMENT_STORE['documents'])} documents")
        debug_log(f"Document store has {len(DOCUMENT_STORE['embeddings'])} embeddings")
        
        if not DOCUMENT_STORE["embeddings"]:
            debug_log("No embeddings in document store - returning empty")
            return [], []
        
        embedding_model = get_embedding_model()
        debug_log("Embedding model loaded")
        
        # Generate embedding for question using SentenceTransformer
        q_embedding = embedding_model.encode(question)
        debug_log(f"Question embedding generated: shape {q_embedding.shape}")
        
        # Calculate similarity with all document embeddings
        embeddings_array = np.array(DOCUMENT_STORE["embeddings"])
        similarities = cosine_similarity([q_embedding], embeddings_array)[0]
        debug_log(f"Calculated similarities: {similarities}")
        
        # Get top_k results
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        debug_log(f"Top indices: {top_indices}")
        
        contexts = []
        sources = []
        
        for idx in top_indices:
            sim_score = similarities[idx]
            debug_log(f"Index {idx}: similarity = {sim_score}")
            if sim_score > 0:  # Only include if there's some similarity
                doc = DOCUMENT_STORE["documents"][idx]
                chunk_text = doc["chunk_text"]
                file_name = doc["file_name"]
                debug_log(f"Adding chunk from {file_name}")
                contexts.append(f"Source: {file_name}\nContent: {chunk_text}")
                sources.append({
                    "file_name": file_name,
                    "source_path": doc.get("source_path", ""),
                    "chunk_preview": chunk_text[:100] + "..." if len(chunk_text) > 100 else chunk_text
                })
        
        debug_log(f"retrieve_context returning {len(contexts)} contexts")
        return contexts, sources
    except Exception as e:
        error_log(f"retrieve_context failed: {str(e)}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise RuntimeError(f"Error retrieving context: {str(e)}")


def answer_question(question: str) -> Tuple[str, List[Dict[str, Any]]]:
    """Answer question using RAG with Google Gemini API"""
    try:
        debug_log(f"answer_question called with: '{question}'")
        
        llm_client = get_llm_client()
        debug_log("Google Gemini client created")
        
        contexts, sources = retrieve_context(question)
        debug_log(f"Retrieved {len(contexts)} contexts and {len(sources)} sources")
        
        # if not contexts:
        #     debug_log("No contexts found - returning fallback message")
        #     return "No relevant documents found for your question.", []
        
        prompt = f"""You are an enterprise RAG assistant.
Use only the supplied context to answer the question.
If the answer is not present in the context, say that you could not find it in the documents.
Keep the answer clear and concise.

Context:
{chr(10).join(contexts)}

Question: {question}"""
        
        debug_log("Prompt prepared, calling Google Gemini API...")
        debug_log(f"API Key exists: {bool(GOOGLE_API_KEY)}")
        debug_log(f"API Key preview: {GOOGLE_API_KEY[:20]}..." if GOOGLE_API_KEY else "No API key")
        debug_log(f"Using model: {GOOGLE_MODEL_NAME}")
        
        response = llm_client.generate_content(prompt)
        debug_log("Google Gemini API response received successfully")
        debug_log(f"Response: {response}")
        
        answer = response.text
        debug_log(f"Answer extracted: {answer}...")
        
        return answer, sources
    except Exception as e:
        error_log(f"answer_question failed: {str(e)}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise RuntimeError(f"Error answering question: {str(e)}")


def validate_credentials() -> Tuple[bool, List[str]]:
    """Validate that all required environment variables are set"""
    required_vars = [
        "GOOGLE_API_KEY",
    ]
    
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        return False, missing_vars
    
    return True, []


def add_documents_to_store(chunks: List[str], file_name: str) -> None:
    """Add document chunks to the in-memory store with embeddings"""
    try:
        debug_log(f"add_documents_to_store called with {len(chunks)} chunks from {file_name}")
        
        embedding_model = get_embedding_model()
        debug_log("Embedding model loaded")
        
        for i, chunk in enumerate(chunks):
            debug_log(f"Processing chunk {i+1}/{len(chunks)} (size: {len(chunk)} chars)")
            embedding = embedding_model.encode(chunk)
            debug_log(f"Generated embedding for chunk {i+1} (shape: {embedding.shape})")
            
            DOCUMENT_STORE["documents"].append({
                "chunk_id": str(uuid.uuid4()),
                "chunk_text": chunk,
                "file_name": file_name,
                "chunk_order": i,
                "source_path": file_name,
                "timestamp": datetime.now().isoformat()
            })
            DOCUMENT_STORE["embeddings"].append(embedding)
        
        debug_log(f"Total documents in store: {len(DOCUMENT_STORE['documents'])}")
        debug_log(f"Total embeddings in store: {len(DOCUMENT_STORE['embeddings'])}")
        debug_log(f"✓ Added {len(chunks)} chunks from {file_name} to document store")
    except Exception as e:
        error_log(f"add_documents_to_store failed: {str(e)}")
        import traceback
        traceback.print_exc(file=sys.stderr)
        raise RuntimeError(f"Error adding documents to store: {str(e)}")
