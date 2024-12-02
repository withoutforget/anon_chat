import copy
from dataclasses import field

from pydantic import BaseModel

from src.model.message import Message


def default_field(obj):
    return field(default_factory=lambda: copy.copy(obj))

class User(BaseModel):
    username: str
    token: str
    public_key: str = ''
    messages: list[Message] = default_field([])

