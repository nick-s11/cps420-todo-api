import pytest
from httpx import AsyncClient
 
 
# Helpers 
async def register(client: AsyncClient, username: str, password: str) -> dict:
    resp = await client.post("/auth/register", json={"username": username, "password": password})
    assert resp.status_code == 201, resp.text
    return resp.json()
 
 
async def login(client: AsyncClient, username: str, password: str) -> str:
    resp = await client.post(
        "/auth/token",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]
 
 
def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
 
 
# Registration tests 
@pytest.mark.asyncio
async def test_register_returns_username_without_password(client: AsyncClient):
    data = await register(client, "alice", "secret123")
    assert data["username"] == "alice"
    assert "hashed_password" not in data
    assert "password" not in data
 
@pytest.mark.asyncio
async def test_duplicate_registration_returns_409(client: AsyncClient):
    await register(client, "alice", "secret123")
    resp = await client.post("/auth/register", json={"username": "alice", "password": "other"})
    assert resp.status_code == 409
 
@pytest.mark.asyncio
async def test_short_password_rejected(client: AsyncClient):
    resp = await client.post("/auth/register", json={"username": "alice", "password": "12"})
    assert resp.status_code == 422
 
 
# Login tests 
@pytest.mark.asyncio
async def test_login_returns_access_token(client: AsyncClient):
    await register(client, "bob", "password99")
    token = await login(client, "bob", "password99")
    assert token and len(token) > 10
 
@pytest.mark.asyncio
async def test_wrong_password_returns_401(client: AsyncClient):
    await register(client, "bob", "password99")
    resp = await client.post(
        "/auth/token",
        data={"username": "bob", "password": "WRONG"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 401
 
 
# Protected endpoint tests 
@pytest.mark.asyncio
async def test_create_todo_without_token_returns_401(client: AsyncClient):
    resp = await client.post("/todos/", json={"title": "test"})
    assert resp.status_code == 401
 
@pytest.mark.asyncio
async def test_create_todo_with_valid_token_returns_201(client: AsyncClient):
    await register(client, "charlie", "pass1234")
    token = await login(client, "charlie", "pass1234")
    resp = await client.post("/todos/", json={"title": "Authenticated todo"}, headers=auth_header(token))
    assert resp.status_code == 201
    assert resp.json()["title"] == "Authenticated todo"
 
@pytest.mark.asyncio
async def test_delete_without_token_returns_401(client: AsyncClient):
    """Even with a valid todo id, delete is blocked without a token."""
    # First create a todo using a valid token
    await register(client, "dave", "pass5678")
    token = await login(client, "dave", "pass5678")
    created = (await client.post("/todos/", json={"title": "to delete"}, headers=auth_header(token))).json()
    todo_id = created["id"]
    # Now attempt deletion without a token
    resp = await client.delete(f"/todos/{todo_id}")
    assert resp.status_code == 401