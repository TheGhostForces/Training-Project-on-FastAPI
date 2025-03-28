from typing import Optional

from pydantic import BaseModel, Field


class TaskSchemaAdd(BaseModel):
    name: str
    description: Optional[str] = Field(None, max_length=300)
    completed: bool = Field(False, title="Статус")

class TaskSchema(TaskSchemaAdd):
    id: int

class UserSchemaAdd(BaseModel):
    username: str
    password: str

class UserSchema(UserSchemaAdd):
    id: int
    role: str

class Universal(BaseModel):
    Ok: bool = True

class UniversalWithId(Universal):
    id: int

class Token(BaseModel):
    access_token: str
    token_type: str

class CurrentPassword(BaseModel):
    current_password: str

class ChangePassword(CurrentPassword):
    new_password: str

class TaskDelete(BaseModel):
    id: int

class UserDelete(BaseModel):
    username: int

class FeedBackAnswer(BaseModel):
    status: str = "sent"

class SaveMessage(BaseModel):
    text: str
    id_user: int
    receiver_username: str