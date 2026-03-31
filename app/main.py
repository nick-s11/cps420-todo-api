from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.connection import database
from app.routers import todos

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect once when the app starts
    await database.connect_to_database()
    try:
        # The application runs while we yield
        yield
    finally:
        # Shutdown: close connections when the app stops
        await database.close_database_connection()


app = FastAPI(
    title="Todo API (MongoDB Atlas + FastAPI)",
    lifespan=lifespan,
)


# Mount the /todos routes
app.include_router(todos.router)