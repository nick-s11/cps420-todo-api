import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://user:password@cluster.mongodb.net/fastapi_db",
)
DATABASE_NAME = "fastapi_db"

MONGO_OPTIONS = {
    "maxPoolSize": 10,
    "serverSelectionTimeoutMS": 5000,
    "socketTimeoutMS": 30000,
}                                                               