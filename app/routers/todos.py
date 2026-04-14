# app/routers/todos.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId

from app.database.connection import database
from app.models.todo import TodoCreate, TodoUpdate, TodoInDB
from fastapi import Depends
from app.routers.auth import get_current_user
from app.models.user import UserPublic
router = APIRouter(prefix="/todos", tags=["todos"])


async def get_todo_collection():
    db = database.db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db["todos"]

@router.get("/", response_model=List[TodoInDB])
async def list_todos(collection=Depends(get_todo_collection)):
    todos: list[TodoInDB] = []
    async for doc in collection.find().sort("_id", -1):
        todos.append(
            TodoInDB(
                id=str(doc["_id"]),
                title=doc.get("title", ""),
                description=doc.get("description"),
                completed=doc.get("completed", False),
            )
        )
    return todos

@router.post("/", response_model=TodoInDB, status_code=status.HTTP_201_CREATED)
async def create_todo(
    todo: TodoCreate,
    collection=Depends(get_todo_collection),
    current_user: UserPublic = Depends(get_current_user),   # ← add this
):
    doc = todo.model_dump()
    result = await collection.insert_one(doc)

    created = await collection.find_one({"_id": result.inserted_id})
    return TodoInDB(
        id=str(created["_id"]),
        title=created.get("title", ""),
        description=created.get("description"),
        completed=created.get("completed", False),
    )

@router.get("/{todo_id}", response_model=TodoInDB)
async def get_todo(
    todo_id: str,
    collection=Depends(get_todo_collection),
):
    if not ObjectId.is_valid(todo_id):
        raise HTTPException(status_code=400, detail="Invalid id format")

    doc = await collection.find_one({"_id": ObjectId(todo_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Todo not found")

    return TodoInDB(
        id=str(doc["_id"]),
        title=doc.get("title", ""),
        description=doc.get("description"),
        completed=doc.get("completed", False),
    )

@router.put("/{todo_id}", response_model=TodoInDB)
async def update_todo(
    todo_id: str,
    update: TodoUpdate,
    collection=Depends(get_todo_collection),
    current_user: UserPublic = Depends(get_current_user),   # ← add this
):
    if not ObjectId.is_valid(todo_id):
        raise HTTPException(status_code=400, detail="Invalid id format")

    update_data = {k: v for k, v in update.model_dump(exclude_unset=True).items()}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await collection.update_one(
        {"_id": ObjectId(todo_id)},
        {"$set": update_data},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")

    doc = await collection.find_one({"_id": ObjectId(todo_id)})
    return TodoInDB(
        id=str(doc["_id"]),
        title=doc.get("title", ""),
        description=doc.get("description"),
        completed=doc.get("completed", False),
    )

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: str,
    collection=Depends(get_todo_collection),
):
    if not ObjectId.is_valid(todo_id):
        raise HTTPException(status_code=400, detail="Invalid id format")

    result = await collection.delete_one({"_id": ObjectId(todo_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Todo not found")

    return None