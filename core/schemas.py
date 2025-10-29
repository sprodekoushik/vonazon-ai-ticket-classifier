# core/schemas.py
from typing import List, Optional
from pydantic import BaseModel, Field

class Ticket(BaseModel):
    id: str
    text: str

class ClassificationRequest(BaseModel):
    tickets: List[Ticket]
    categories: List[str]
    model: str = "deepseek-chat"
    temperature: float = 0.0

class ClassificationResult(BaseModel):
    ticket_id: str
    ticket_text: str
    category: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    explanation: Optional[str] = None
