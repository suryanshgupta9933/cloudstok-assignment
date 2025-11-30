from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

from src.agents.agent import run_agent
from src.schemas.models import AgentResult

load_dotenv()

app = FastAPI(title="Customer Support Agent API")

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]

@app.post("/chat", response_model=AgentResult)
async def chat(request: ChatRequest):
    """
    Endpoint to interact with the Customer Support Agent.
    """
    try:
        result = run_agent(request.messages)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
