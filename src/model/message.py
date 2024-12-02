from pydantic import BaseModel

class Message(BaseModel):
    timestamp: int
    from_username: str
    text: str