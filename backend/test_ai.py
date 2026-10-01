import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(PROJECT_ROOT / ".env")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY was not found in E:\\ai-commerce-agent\\.env"
    )

print("Groq API key loaded successfully.")
print("Key prefix:", api_key[:8])


client = Groq(
    api_key=api_key
)


response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Reply with exactly: AI connection successful"
        }
    ]
)

print(response.choices[0].message.content)