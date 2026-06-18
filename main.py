from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "success": True,
        "message": "Backend running"
    }

# Existing endpoint (keep this)
@app.post("/chat")
def chat(data: dict):

    messages = data.get("messages", [])

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=messages,
        max_tokens=500
    )

    return {
        "success": True,
        "message": {
            "role": "assistant",
            "content": response.choices[0].message.content
        }
    }

# New streaming endpoint
@app.post("/chat-stream")
def chat_stream(data: dict):

    messages = data.get("messages", [])

    def generate():

        stream = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=messages,
            max_tokens=500,
            stream=True
        )

        for chunk in stream:

            if not chunk.choices:
                continue

            delta = chunk.choices[0].delta

            if delta and delta.content:
                yield delta.content

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )