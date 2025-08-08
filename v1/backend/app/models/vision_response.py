from pydantic import BaseModel
from typing import List, Optional

class MessageContent(BaseModel):
    content: str

class Choice(BaseModel):
    message: MessageContent

class OpenRouterResponse(BaseModel):
    choices: List[Choice]
