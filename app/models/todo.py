# app/models/todo.py
from typing import Optional
from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    completed: bool = False


class TodoCreate(TodoBase):
    """Shape of data when creating a new todo."""
    pass


class TodoUpdate(BaseModel):
    """Fields that can be updated; all optional."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoInDB(TodoBase):
    """What a todo looks like when we read it from the database."""
    id: str = Field(..., description="MongoDB document id as a string")