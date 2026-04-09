from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx  # Faster and non-blocking
import asyncio

app = FastAPI()

class PromptRequest(BaseModel):
    system: str
    prompt: str

@app.post("/generate")
async def generate_response(request: PromptRequest):
    # 'localhost' is reliable for internal container communication
    url = "http://localhost:11434/api/chat"
    
    payload = {
        "model": "qwen2.5:1.5b",
        "messages": [
            {"role": "system", "content": request.system},
            {"role": "user", "content": request.prompt}
        ],
        "stream": False,
        "keep_alive": 0  
    }
    
    # Use an async client to keep the server responsive
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(url, json=payload)
            
            # Check if model isn't pulled yet
            if response.status_code == 404:
                raise HTTPException(status_code=503, detail="Model still downloading or not found.")
                
            response.raise_for_status()
            data = response.json()
            return {"response": data.get("message", {}).get("content")}
            
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Ollama server is booting up. Please wait.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM Error: {str(e)}")

@app.get("/health")
async def health():
    return {"status": "alive"}