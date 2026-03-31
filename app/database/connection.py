from pymongo import AsyncMongoClient
from app.config.database import MONGODB_URI, DATABASE_NAME, MONGO_OPTIONS


class Database:
    """Database connection manager."""

    client: AsyncMongoClient | None = None
    db = None

    async def connect_to_database(self):
        # Create client and force initial connection
        self.client = AsyncMongoClient(MONGODB_URI, **MONGO_OPTIONS)
        await self.client.aconnect()
        self.db = self.client[DATABASE_NAME]
        print("Connected to MongoDB!")

    async def close_database_connection(self):
        if self.client:
            await self.client.close()
            print("Closed MongoDB connection!")


database = Database()