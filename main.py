from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
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

def get_system_message():
    today = datetime.now().strftime("%A, %B %d, %Y")
    return {
        "role": "system",
        "content": f"You are a helpful assistant. Today's date is {today}."
    }

@app.get("/")
def home():
    return {"success": True, "message": "Backend running"}

@app.post("/chat")
def chat(data: dict):
    messages = data.get("messages", [])

    # Prepend system message with today's date
    messages_with_system = [get_system_message()] + messages

    response = client.chat.completions.create(
        model="google/gemini-2.5-flash",
        messages=messages_with_system,
        max_tokens=500
    )

    return {
        "success": True,
        "message": {
            "role": "assistant",
            "content": response.choices[0].message.content
        }
    }

@app.post("/chat-stream")
def chat_stream(data: dict):
    messages = data.get("messages", [])

    # Prepend system message with today's date
    messages_with_system = [get_system_message()] + messages

    def generate():
        stream = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=messages_with_system,
            max_tokens=500,
            stream=True
        )

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content

    return StreamingResponse(generate(), media_type="text/plain")