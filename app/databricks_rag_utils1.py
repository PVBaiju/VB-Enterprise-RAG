import os
import faiss
import pandas as pd
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_MODEL_NAME = os.getenv("GOOGLE_MODEL_NAME","gemini-2.5-flash")

genai.configure(api_key=GOOGLE_API_KEY)

index = faiss.read_index("docs.index")
meta = pd.read_pickle("metadata.pkl")


def validate_credentials():

    missing = []

    if not GOOGLE_API_KEY:
        missing.append("GOOGLE_API_KEY")

    return len(missing)==0, missing


def answer_question(question):

    q = genai.embed_content(
        model="models/gemini-embedding-2",
        content=question,
        task_type="RETRIEVAL_QUERY"
    )["embedding"]

    q = np.array([q]).astype("float32")

    D, I = index.search(q, 4)

    context = ""
    sources = []

    for idx in I[0]:

        row = meta.iloc[idx]

        context += row["chunk_text"] + "\n\n"

        sources.append({
            "file_name": row["file_name"],
            "chunk_preview": row["chunk_text"][:250]
        })

    prompt = f"""
Use only context.

Context:
{context}

Question:
{question}
"""

    res = genai.GenerativeModel(
        GOOGLE_MODEL_NAME
    ).generate_content(prompt)

    return res.text, sources