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
def generate():
    yield "FASTAPI_TEST_123"

@app.get("/")
def home():
    return {
        "success": True,
        "message": "Backend running"
    }


@app.post("/chat")
def chat(data: dict):

    user_messages = data.get("messages", [])

    messages = [
        {
            "role": "system",
            "content": f"""
You are a helpful AI assistant.

Today's date is {datetime.now().strftime('%B %d, %Y')}.

If asked about today's date, use the date above.
"""
        }
    ] + user_messages

    try:

        response = client.chat.completions.create(
            model="google/gemini-2.5-flash",
            messages=messages,
            max_tokens=500
        )

        return {
            "success": True,
            "model": response.model,
            "message": {
                "role": "assistant",
                "content": response.choices[0].message.content
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.post("/chat-stream")
def chat_stream(data: dict):

    def generate():
        yield "FASTAPI_TEST_123"

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )