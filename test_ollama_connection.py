#!/usr/bin/env python3
"""
Test script to verify Ollama connection and model availability
"""

from openai import OpenAI
import json

# Test the main model
print("Testing Ollama connection...")
print("=" * 50)

try:
    client = OpenAI(
        api_key="ollama",  # Ollama doesn't require a real API key
        base_url="http://172.30.1.14:11434/v1"
    )
    
    print("1. Testing chat completion with gemma3:27b-it-qat...")
    response = client.chat.completions.create(
        model="gemma3:27b-it-qat",
        messages=[
            {"role": "user", "content": "Hello! Please respond with a simple greeting."}
        ],
        max_tokens=50
    )
    
    print(f"✅ Chat completion successful!")
    print(f"Response: {response.choices[0].message.content}")
    print()
    
except Exception as e:
    print(f"❌ Chat completion failed: {e}")
    print()

# Test embeddings
try:
    print("2. Testing embeddings with nomic-embed-text:latest...")
    response = client.embeddings.create(
        model="nomic-embed-text:latest",
        input=["Hello world"]
    )
    
    print(f"✅ Embeddings successful!")
    print(f"Embedding dimension: {len(response.data[0].embedding)}")
    print(f"First 5 values: {response.data[0].embedding[:5]}")
    print()
    
except Exception as e:
    print(f"❌ Embeddings failed: {e}")
    print()

print("=" * 50)
print("Test completed!")