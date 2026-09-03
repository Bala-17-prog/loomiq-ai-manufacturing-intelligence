from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.dependencies import get_db
from backend.ai.copilot import CopilotEngine

router = APIRouter(prefix="/api/copilot", tags=["AI Copilot"])

class CopilotQuery(BaseModel):
    query: str

@router.post("/ask")
def ask_copilot(payload: CopilotQuery, db: Session = Depends(get_db)):
    engine = CopilotEngine(db)
    response = engine.ask(payload.query)
    return response
