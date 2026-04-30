import os
import numpy as np
import pandas as pd
import faiss
import google.generativeai as genai
from dotenv import load_dotenv
from groq import Groq

load_dotenv(override=True)

# ---------------- ENV ----------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_MODEL_NAME = os.getenv("GOOGLE_MODEL_NAME", "gemini-2.5-flash")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")

if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(__file__)
INDEX_PATH = os.path.join(BASE_DIR, "docs.index")
META_PATH = os.path.join(BASE_DIR, "metadata.pkl")

index = None
metadata = None


# ---------------- LOAD FAISS ----------------
def load_faiss():
    global index, metadata

    if index is not None and metadata is not None:
        return

    index = faiss.read_index(INDEX_PATH)
    metadata = pd.read_pickle(META_PATH)


# ---------------- EMBEDDINGS ----------------
def get_embedding(text):
    r = genai.embed_content(
        model="models/gemini-embedding-2",
        content=text,
        task_type="RETRIEVAL_QUERY"
    )
    return np.array(r["embedding"], dtype="float32")


# ---------------- SEARCH (IMPROVED) ----------------
def search_chunks(question, top_k=12):   # 🔥 increased from 6 → 12

    load_faiss()

    query_vec = get_embedding(question).reshape(1, -1)
    distances, indices = index.search(query_vec, top_k)

    results = []

    for i in indices[0]:
        row = metadata.iloc[i]

        results.append({
            "file_name": row["file_name"],
            "chunk_text": row["chunk_text"]   # 🔥 no heavy slicing here
        })

    return pd.DataFrame(results)


# ---------------- LLM ----------------
def ask_gemini(prompt):
    model = genai.GenerativeModel(GOOGLE_MODEL_NAME)
    return model.generate_content(prompt).text


def ask_groq(prompt):
    if not groq_client:
        raise Exception("Groq not configured")

    res = groq_client.chat.completions.create(
        model=GROQ_MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )
    return res.choices[0].message.content


def ask_llm(prompt):
    try:
        return ask_gemini(prompt)
    except:
        return ask_groq(prompt)


# ---------------- MAIN QA ----------------
def answer_question(question):

    df = search_chunks(question, top_k=12)

    context = "\n\n".join(df["chunk_text"].tolist())

    sources = []

    for _, row in df.iterrows():
        sources.append({
            "file_name": row["file_name"],
            "chunk_preview": row["chunk_text"][:150]
        })

    # ✅ FIXED PROMPT (NOW question is valid here)
    prompt = f"""
You are a precise HR policy assistant.

RULES:
- Only return relevant section for the query
- Do NOT include full handbook
- Do NOT mix unrelated policies
- Keep response structured and clean

OUTPUT FORMAT:

📌 {question}

- Relevant points only
- Clear bullets
- No extra sections

Context:
{context}

Question:
{question}

FINAL ANSWER:
"""

    answer = ask_llm(prompt)

    return answer.strip(), sources