from fastapi import FastAPI
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(
            OPENAI_BASE_URL,
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "content-type": "application/json",
                "HTTP-Referer": "http://localhost",
                "X-Title": "Gen AI App",
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": f"<s>[INST]{req.message}[/INST]"
                    },
                ],
            },
            timeout=30,
        )
        data = response.json()

        if "choices" not in data:
            return {
                "error": "OpenRouter API error",
                "raw_response": data
            }
        content = data["choices"][0]["message"]["content"]
        return {
            "status": "success",
            "data": {
                "text": content
            },
            "meta": {
                "model": data.get("model"),
                "provider": data.get("provider"),
                "total_tokens": data.get("usage", {}).get("total_tokens")
            }
        }