#!/usr/bin/env python3
"""
Check available embedding models in Google Generative AI API
"""

import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("❌ GOOGLE_API_KEY not set in .env")
    exit(1)

genai.configure(api_key=api_key)

print("🔍 Checking available models for embedContent...\n")

try:
    models = genai.list_models()
    embedding_models = [m for m in models if 'embed' in m.name.lower()]

    if embedding_models:
        print("✅ Available embedding models:\n")
        for model in embedding_models:
            print(f"  • {model.name}")
            print(f"    Display name: {model.display_name}")
            # Check if embedContent is supported
            if hasattr(model, 'supported_generation_methods'):
                methods = model.supported_generation_methods
                if 'embedContent' in methods:
                    print(f"    ✓ Supports: embedContent")
            print()
    else:
        print("❌ No embedding models found")
        print("\nAll available models:")
        for model in models:
            print(f"  • {model.name}")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTry using: models/embedding-gecko-002")
