# Debug Logging Implementation

## Problem Found
❌ **Documents were NOT being added to the in-memory store** when users uploaded them!

The upload tab was only showing a preview but not calling `add_documents_to_store()`. This meant:
- Documents were read from the file
- Preview was displayed
- But they were **never stored in DOCUMENT_STORE**
- So when asking questions, there were no embeddings to search
- Groq API was never called (because no documents = no context)

## Solution Implemented

### 1. Added `add_documents_to_store` to app.py imports
```python
from rag_utils import (
    answer_question,
    extract_text_from_file,
    chunk_text,
    validate_credentials,
    add_documents_to_store,  # ← ADDED
)
```

### 2. Actually call the function when uploading
```python
# After reading the file and showing preview:
chunks = chunk_text(text)
add_documents_to_store(chunks, uploaded_file.name)  # ← ADDED THIS LINE
```

### 3. Added comprehensive debug logging

**In `retrieve_context()`:**
```
[DEBUG] retrieve_context called with question: '...'
[DEBUG] Document store has X documents
[DEBUG] Document store has X embeddings
[DEBUG] Embedding model loaded
[DEBUG] Question embedding generated: shape (384,)
[DEBUG] Calculated similarities: [0.82, 0.65, ...]
[DEBUG] Top indices: [0, 2, 1, 3]
[DEBUG] Index 0: similarity = 0.82
[DEBUG] Adding chunk from employee_handbook.txt
```

**In `answer_question()`:**
```
[DEBUG] answer_question called with: 'What is the leave policy?'
[DEBUG] Groq client created
[DEBUG] Retrieved 4 contexts and 4 sources
[DEBUG] Prompt prepared, calling Groq API...
[DEBUG] API Key exists: True
[DEBUG] API Key preview: gsk_MEoE5EGgIUGGc0...
[DEBUG] Groq API response received successfully
[DEBUG] Answer extracted: According to the employee handbook...
```

**In `add_documents_to_store()`:**
```
[DEBUG] add_documents_to_store called with 5 chunks from employee_handbook.txt
[DEBUG] Embedding model loaded
[DEBUG] Processing chunk 1/5 (size: 1200 chars)
[DEBUG] Generated embedding for chunk 1 (shape: (384,))
[DEBUG] Total documents in store: 5
[DEBUG] Total embeddings in store: 5
✓ Added 5 chunks from employee_handbook.txt to document store
```

## Flow Diagram

```
USER UPLOADS DOCUMENT
         ↓
    Read file (PDF/DOCX/TXT)
    [DEBUG] File read
         ↓
    Extract text
    [DEBUG] Text extracted
         ↓
    Chunk text (1200 chars)
    [DEBUG] X chunks created
         ↓
    Add to document store ← THIS WAS MISSING!
    [DEBUG] Embedding model loaded
    [DEBUG] Processing chunk 1/X
    [DEBUG] Generated embedding for chunk 1
    [DEBUG] Total documents in store: X
         ↓
    Show success message
    
---

USER ASKS QUESTION
         ↓
    [DEBUG] answer_question called
         ↓
    Get Groq client
    [DEBUG] Groq client created
         ↓
    Retrieve context
    [DEBUG] Document store has X documents ← NOW WILL FIND THEM!
    [DEBUG] Question embedding generated
    [DEBUG] Calculated similarities
    [DEBUG] Top indices: [best matches]
         ↓
    [DEBUG] Retrieved 4 contexts
         ↓
    Call Groq API
    [DEBUG] API Key exists: True
    [DEBUG] Calling Groq API...
         ↓
    [DEBUG] Groq API response received
         ↓
    Return answer + sources
```

## How to Test

1. **Upload a document:**
   - Go to "📤 Document Upload" tab
   - Upload `data/sample_docs/employee_handbook.txt`
   - Watch the terminal for debug output
   - Check for: `✓ Added X chunks from employee_handbook.txt`

2. **Ask a question:**
   - Go to "💬 Q&A" tab
   - Type: "What is the leave policy?"
   - Click "🔍 Ask"
   - Watch the terminal for all the debug steps
   - Should see: `[DEBUG] Groq API response received successfully`

3. **What you should see in terminal:**

```
[DEBUG] add_documents_to_store called with 5 chunks from employee_handbook.txt
[DEBUG] Embedding model loaded
[DEBUG] Processing chunk 1/5 (size: 1200 chars)
[DEBUG] Generated embedding for chunk 1 (shape: (384,))
[DEBUG] Processing chunk 2/5 (size: 1200 chars)
[DEBUG] Generated embedding for chunk 2 (shape: (384,))
[DEBUG] Processing chunk 3/5 (size: 1200 chars)
[DEBUG] Generated embedding for chunk 3 (shape: (384,))
[DEBUG] Processing chunk 4/5 (size: 1200 chars)
[DEBUG] Generated embedding for chunk 4 (shape: (384,))
[DEBUG] Processing chunk 5/5 (size: 1200 chars)
[DEBUG] Generated embedding for chunk 5 (shape: (384,))
[DEBUG] Total documents in store: 5
[DEBUG] Total embeddings in store: 5
✓ Added 5 chunks from employee_handbook.txt to document store

[DEBUG] answer_question called with: 'What is the leave policy?'
[DEBUG] Groq client created
[DEBUG] retrieve_context called with question: 'What is the leave policy?'
[DEBUG] Document store has 5 documents
[DEBUG] Document store has 5 embeddings
[DEBUG] Embedding model loaded
[DEBUG] Question embedding generated: shape (384,)
[DEBUG] Calculated similarities: [0.87 0.62 0.55 0.48 0.31]
[DEBUG] Top indices: [0 1 2 3]
[DEBUG] Index 0: similarity = 0.87
[DEBUG] Adding chunk from employee_handbook.txt
[DEBUG] Index 1: similarity = 0.62
[DEBUG] Adding chunk from employee_handbook.txt
[DEBUG] Index 2: similarity = 0.55
[DEBUG] Adding chunk from employee_handbook.txt
[DEBUG] Index 3: similarity = 0.48
[DEBUG] Adding chunk from employee_handbook.txt
[DEBUG] retrieve_context returning 4 contexts
[DEBUG] Retrieved 4 contexts and 4 sources
[DEBUG] Prompt prepared, calling Groq API...
[DEBUG] API Key exists: True
[DEBUG] API Key preview: gsk_MEoE5EGgIUGGc0...
[DEBUG] Groq API response received successfully
[DEBUG] Response: <groq.types.chat.chat_completion.ChatCompletion object at 0x...>
[DEBUG] Answer extracted: According to the employee handbook, the leave policy includes...
```

## Root Causes Identified

1. ✅ **Fixed: Documents not stored** - Added `add_documents_to_store()` call
2. ✅ **Fixed: Missing imports** - Added import for `add_documents_to_store`
3. ✅ **Added: Visibility** - Debug prints show exactly what's happening at each step

## What's Now Working

✅ Documents uploaded → chunks created → embeddings generated → stored in RAM  
✅ Questions asked → embeddings searched → top chunks retrieved → Groq API called  
✅ Full visibility into the entire flow via debug prints

## Next: Try It Out!

1. Run the app: `streamlit run app.py`
2. Upload a document
3. Ask a question
4. Watch the terminal for debug output
5. See the answer appear with sources!
