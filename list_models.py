#!/usr/bin/env python3
"""List available Google Gemini models"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, '/home/arunkumar/Documents/CODE/enterprise-rag-databricks/app')
os.chdir('/home/arunkumar/Documents/CODE/enterprise-rag-databricks/app')

load_dotenv('.env')

import google.generativeai as genai

api_key = os.environ.get('GOOGLE_API_KEY')
print(f"\n[DEBUG] Using API key: {api_key[:30]}...\n")

genai.configure(api_key=api_key)

print("=" * 60)
print("Available Google Gemini Models")
print("=" * 60 + "\n")

models = genai.list_models()
free_models = []

for model in models:
    # Check if model supports generateContent'
    print(model)
    

print("\n" + "=" * 60)
print("Recommended Free Models:")
print("=" * 60 + "\n")

for model in free_models:
    print(f"  - {model}")

if free_models:
    recommended = free_models[0]
    print(f"\n✓ Using: {recommended}")
    print(f"\nUpdate your .env file:")
    print(f"  GOOGLE_MODEL_NAME={recommended}")
