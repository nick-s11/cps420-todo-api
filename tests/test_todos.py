# tests/test_todos.py

import pytest
from httpx import AsyncClient

# Helpers 

async def create_todo(client: AsyncClient, title: str, description: str = None) -> dict:
    """Convenience function: POST a todo and return the response JSON."""
    payload = {"title": title}
    if description:
        payload["description"] = description
    resp = await client.post("/todos/", json=payload)
    assert resp.status_code == 201, f"Setup failed: {resp.text}"
    return resp.json()


# Create

@pytest.mark.asyncio
async def test_create_todo_returns_201_with_fields(client: AsyncClient):
    """POST /todos/ with valid data returns 201 and all expected fields."""
    payload = {"title": "Buy groceries", "description": "Milk and eggs"}
    response = await client.post("/todos/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk and eggs"
    assert data["completed"] is False
    assert "id" in data        # MongoDB assigns an ObjectId


@pytest.mark.asyncio
async def test_create_todo_defaults_completed_to_false(client: AsyncClient):
    """A newly created todo is not completed unless specified."""
    data = await create_todo(client, "Exercise")
    assert data["completed"] is False


@pytest.mark.asyncio
async def test_create_todo_empty_title_rejected(client: AsyncClient):
    """
    POST /todos/ with an empty string title violates the min_length=1
    constraint on TodoBase and should return 422 Unprocessable Entity.
    """
    response = await client.post("/todos/", json={"title": ""})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_todo_missing_title_rejected(client: AsyncClient):
    """POST /todos/ with no title field at all returns 422."""
    response = await client.post("/todos/", json={"description": "No title here"})
    assert response.status_code == 422


# List

@pytest.mark.asyncio
async def test_list_todos_empty_at_start(client: AsyncClient):
    """GET /todos/ on a freshly cleared collection returns an empty list."""
    response = await client.get("/todos/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_todos_returns_all_created(client: AsyncClient):
    """After creating three todos, GET /todos/ returns all three."""
    await create_todo(client, "Task A")
    await create_todo(client, "Task B")
    await create_todo(client, "Task C")

    response = await client.get("/todos/")
    assert response.status_code == 200
    titles = [t["title"] for t in response.json()]
    assert "Task A" in titles
    assert "Task B" in titles
    assert "Task C" in titles


@pytest.mark.asyncio
async def test_list_todos_each_item_has_required_fields(client: AsyncClient):
    """Every item in the list response has id, title, description, completed."""
    await create_todo(client, "Check fields")
    items = (await client.get("/todos/")).json()
    for item in items:
        assert "id" in item
        assert "title" in item
        assert "description" in item
        assert "completed" in item


# Get by ID

@pytest.mark.asyncio
async def test_get_todo_by_id_returns_correct_todo(client: AsyncClient):
    """GET /todos/{id} returns only the todo with that id."""
    created = await create_todo(client, "Walk the dog")
    todo_id = created["id"]

    response = await client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Walk the dog"


@pytest.mark.asyncio
async def test_get_todo_invalid_id_format_returns_400(client: AsyncClient):
    """
    GET /todos/{id} with a string that is not a valid ObjectId returns 400.
    The router validates the id format before querying MongoDB.
    """
    response = await client.get("/todos/not-a-valid-objectid")
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_todo_valid_id_not_found_returns_404(client: AsyncClient):
    """GET /todos/{id} with a properly formatted but non-existent id returns 404."""
    fake_id = "000000000000000000000001"   # valid ObjectId format, does not exist
    response = await client.get(f"/todos/{fake_id}")
    assert response.status_code == 404


# Update

@pytest.mark.asyncio
async def test_update_todo_marks_completed(client: AsyncClient):
    """PUT /todos/{id} with completed=true updates that field."""
    created = await create_todo(client, "Read chapter 12")
    todo_id = created["id"]

    response = await client.put(f"/todos/{todo_id}", json={"completed": True})
    assert response.status_code == 200
    assert response.json()["completed"] is True


@pytest.mark.asyncio
async def test_update_todo_changes_title(client: AsyncClient):
    """PUT /todos/{id} can update the title field."""
    created = await create_todo(client, "Old title")
    todo_id = created["id"]

    response = await client.put(f"/todos/{todo_id}", json={"title": "New title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New title"


@pytest.mark.asyncio
async def test_update_todo_preserves_untouched_fields(client: AsyncClient):
    """Updating one field with exclude_unset=True must not reset other fields."""
    created = await create_todo(client, "Keep my description", "important note")
    todo_id = created["id"]

    # Only update completed; description must stay intact
    await client.put(f"/todos/{todo_id}", json={"completed": True})
    response = await client.get(f"/todos/{todo_id}")
    assert response.json()["description"] == "important note"


@pytest.mark.asyncio
async def test_update_todo_empty_body_returns_400(client: AsyncClient):
    """
    PUT /todos/{id} with an empty JSON body should return 400 because
    there is nothing to update and the schema requires at least one field.
    """
    created = await create_todo(client, "Needs update")
    todo_id = created["id"]

    response = await client.put(f"/todos/{todo_id}", json={})
    assert response.status_code == 400
