<<<<<<< HEAD
# Enterprise Document Q&A Assistant

## Quick Start (5 Minutes)

### 1. Get Groq API Key
```bash
# Visit https://console.groq.com
# Sign up → Create API key → Copy key (starts with "gsk_")
```

### 2. Configure
```bash
cp app/.env.sample app/.env
# Edit app/.env and add your Groq API key
```

### 3. Install
```bash
cd app
pip install -r requirements.txt
```

### 4. Run
```bash
streamlit run app.py
```

### 5. Test
- Open http://localhost:8501
- Upload `data/sample_docs/employee_handbook.txt`
- Ask: "What is the leave policy?"
- See answer in ~2 seconds

---

## Features

✅ **Document Upload** - PDF, DOCX, TXT support  
✅ **Semantic Search** - Find relevant sections  
✅ **Groq AI LLM** - Ultra-fast answers  
✅ **Free Embeddings** - No API key needed  
✅ **Local Storage** - RAM-based (no cloud)  
✅ **Query History** - Track past questions  

---

## Architecture

```
Upload Document
    ↓
Extract Text (PDF/DOCX/TXT)
    ↓
Split into Chunks (1200 chars with overlap)
    ↓
Generate Embeddings (SentenceTransformers - free)
    ↓
Store in Memory (DOCUMENT_STORE)
    ↓
[User asks question]
    ↓
Generate Question Embedding
    ↓
Find Similar Chunks (Cosine Similarity)
    ↓
Send Top 4 Chunks to Groq AI
    ↓
LLM generates answer using context
    ↓
Display answer + sources
```

---

## Environment Variables

Only **one** variable needed:

```bash
GROQ_API_KEY=gsk_your_key_here
```

Get it from: https://console.groq.com

---

## File Structure

```
enterprise-rag-databricks/
├── README.md                    ← You are here
├── GROQ_SETUP.md               ← Groq setup guide
├── GROQ_LOCAL_VERSION.md       ← Detailed architecture
├── MIGRATION_STATUS.md         ← What was changed
│
├── app/
│   ├── app.py                  ← Streamlit web interface
│   ├── rag_utils.py            ← RAG logic (embeddings, search, LLM)
│   ├── requirements.txt        ← Dependencies
│   └── .env.sample             ← Configuration template
│
├── data/
│   └── sample_docs/
│       └── employee_handbook.txt  ← Test document
│
└── notebooks/
    └── (Migration notebooks - for reference only)
```

---

## Dependencies

| Package | Size | Purpose |
|---------|------|---------|
| streamlit | 20MB | Web UI |
| groq | 5MB | LLM API client |
| sentence-transformers | 50MB | Embeddings (free) |
| torch | 400MB | Neural networks |
| pypdf | 5MB | PDF reading |
| python-docx | 2MB | DOCX reading |
| scikit-learn | 5MB | Similarity search |
| numpy | 10MB | Math operations |
| **Total** | **~500MB** | One-time download |

---

## Troubleshooting

### Issue: "GROQ_API_KEY not found"
```bash
# Make sure .env file exists in app/ directory
ls app/.env

# Check it has your key
cat app/.env | grep GROQ
```

### Issue: Slow first upload
- **Normal!** First time takes 30-60 seconds (downloads models)
- Subsequent uploads: 5-10 seconds

### Issue: "Cannot import groq"
```bash
# Reinstall dependencies
cd app
pip install --upgrade -r requirements.txt
```

---

## Performance

| Operation | Time |
|-----------|------|
| Upload document (first time) | 30-60s |
| Upload document (subsequent) | 5-10s |
| Generate answer | 1-2s |
| Search documents | <1s |

---

## Cost Breakdown

| Component | Cost |
|-----------|------|
| One-time download | $0 |
| Monthly API | $0 (Groq free tier) |
| Storage | $0 (local RAM) |
| **Total** | **$0 forever** |

---

## For Databricks Migration

See `MIGRATION_STATUS.md` for:
- What was removed
- What was added
- How to upgrade back to Databricks version

---

## Support

- 📖 **Setup Issues?** → See `GROQ_SETUP.md`
- 🏗️ **Architecture Questions?** → See `GROQ_LOCAL_VERSION.md`
- 🔄 **Migrating from Databricks?** → See `MIGRATION_STATUS.md`

---

**Status**: ✅ Production Ready (Development/Testing)  
**Last Updated**: April 2026  
**Version**: 1.0
=======

# Enterprise-RAG-Document Q&A Assistant
<img width="1536" height="1024" alt="Arch Diagram + Flow" src="https://github.com/user-attachments/assets/90938e47-33b5-47a9-9497-8aed1806987a" />

GENAI project--employee policy details

>>>>>>> cd929e96bac6867b2bd823522ac471b592667ba9
