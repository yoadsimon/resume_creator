#!/usr/bin/env python3
"""OpenAI client and utility functions."""

import os
import json
import time
import openai
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables - handle missing .env gracefully
try:
    load_dotenv()
except Exception:
    pass  # Environment variables will be loaded from system/docker environment


class OpenAIClient():
    def __init__(self, model="gpt-4-turbo-preview"):
        self.client = OpenAI(
            organization=os.getenv('OPEN_AI_ORGANIZATION_ID'),
            project=os.getenv('OPEN_AI_PROJECT_ID'),
            api_key=os.getenv('OPEN_AI_TOKEN')
        )
        self.model = model
        self.max_retries = 3
        self.retry_delay = 1

    def generate_text(self, prompt, model=None, temperature=None):
        model = model or self.model
        attempt = 0
        
        while attempt < self.max_retries:
            try:
                params = {
                    "messages": [{"role": "user", "content": prompt}],
                    "model": model
                }
                # Only add temperature for models that support it
                if temperature and "gpt-4-turbo" not in model:
                    params["temperature"] = temperature
                    
                response = self.client.chat.completions.create(**params)
                return response.choices[0].message.content
            except Exception as e:
                attempt += 1
                if attempt == self.max_retries:
                    print(f"Error after {self.max_retries} attempts: {e}")
                    return None
                print(f"Attempt {attempt} failed: {e}. Retrying...")
                time.sleep(self.retry_delay * attempt)


