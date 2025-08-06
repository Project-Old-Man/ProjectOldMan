from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    category: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    category: str
