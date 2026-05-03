"""
main.py — Madison Agent
FastAPI application exposing the agent as a REST API.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

from agent import run_agent
from models import AnalyzeRequest, AnalyzeResponse, AgentResult

app = FastAPI(
    title="Madison Agent",
    description="Autonomous enterprise data extraction agent powered by Claude.",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok", "agent": "Madison Agent", "version": "1.0.0"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    try:
        raw_result = run_agent(request.username)
        result = AgentResult(**raw_result)
        return AnalyzeResponse(success=True, data=result)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Agent returned malformed JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)