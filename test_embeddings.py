#!/usr/bin/env python3
import os
import sys

# Add app to path
sys.path.insert(0, '/home/arunkumar/Documents/CODE/enterprise-rag-databricks/app')
os.chdir('/home/arunkumar/Documents/CODE/enterprise-rag-databricks/app')

from dotenv import load_dotenv
load_dotenv('.env')

from rag_utils import get_embedding_model, chunk_text, add_documents_to_store, DOCUMENT_STORE

print("\n=== Testing Embedding Model ===", file=sys.stderr)
model = get_embedding_model()
print("✓ Embedding model loaded successfully", file=sys.stderr)

print("\n=== Testing Chunk Creation ===", file=sys.stderr)
text = "Leave policy: 20 days annual. " * 50
chunks = chunk_text(text)
print(f"✓ Created {len(chunks)} chunks", file=sys.stderr)

print("\n=== Testing Document Store ===", file=sys.stderr)
add_documents_to_store(chunks, "test.txt")
print(f"✓ Documents in store: {len(DOCUMENT_STORE['documents'])}", file=sys.stderr)
print(f"✓ Embeddings in store: {len(DOCUMENT_STORE['embeddings'])}", file=sys.stderr)

print("\n=== All tests passed! ===\n", file=sys.stderr)
