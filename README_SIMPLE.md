# Enterprise RAG Assistant - Streamlit App

A Document Q&A system using Databricks, Azure OpenAI, and Streamlit.

## 📋 Prerequisites

```bash
Python 3.10+
pip
```

## 🚀 How to Run Locally

### 1. Clone & Navigate
```bash
cd enterprise-rag-databricks/app
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create .env File
```bash
cp .env.sample .env
```

Edit `.env` with your credentials:
```
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_key
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
DATABRICKS_HOST=https://adb-xxxx.azuredatabricks.net
DATABRICKS_TOKEN=dapi_your_token
VECTOR_SEARCH_ENDPOINT=rag-demo-endpoint
VECTOR_INDEX_NAME=main.rag_demo.docs_index
```

### 5. Run Streamlit App
```bash
streamlit run app.py
```

App opens at: `http://localhost:8501`

---

## 📂 File Structure

```
app/
├── app.py                 # Main Streamlit app
├── rag_utils.py          # RAG functions
├── requirements.txt       # Dependencies
├── .env.sample           # Credentials template
└── .streamlit/
    └── config.toml       # Streamlit config
```

---

## 🎯 Features

✅ **Q&A Tab** - Ask questions about documents
✅ **Upload Tab** - Upload & preview files (PDF, DOCX, TXT)
✅ **Help Tab** - Documentation & examples

---

## 🧠 How It Works

1. **Upload Document** → Extract text
2. **Chunk Text** → Split into 1200-char pieces
3. **Generate Embeddings** → Azure OpenAI
4. **Store in Vector Index** → Databricks
5. **Ask Question** → Search similar chunks
6. **Generate Answer** → Azure OpenAI LLM

---

## 📊 Databricks Setup (First Time)

Run these notebooks in order:
1. `01_config_and_setup.py` - Create tables
2. `02_ingest_documents.py` - Upload documents
3. `03_chunk_documents.py` - Split into chunks
4. `04_generate_embeddings_and_index.py` - Create vector index
5. `05_query_test.py` - Test the system

---

## 🆘 Troubleshooting

**ModuleNotFoundError**: Run `pip install -r requirements.txt`

**Missing .env**: Create it from `.env.sample`

**Connection errors**: Check credentials in `.env`

**No search results**: Ensure Databricks notebooks ran successfully

---

## 📝 Example Environment

```
AZURE_OPENAI_ENDPOINT=https://openai-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=sk-abc123xyz...
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-3-small
DATABRICKS_HOST=https://adb-1234567890abcdef.azuredatabricks.net
DATABRICKS_TOKEN=dapi123456789abcdef
VECTOR_SEARCH_ENDPOINT=rag-demo-endpoint
VECTOR_INDEX_NAME=main.rag_demo.docs_index
```

---

**That's it! Run `streamlit run app.py` and go.**
