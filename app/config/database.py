import os
from dotenv import load_dotenv
 
load_dotenv()   # reads .env for local development; no-op when env vars are already set
 
MONGODB_URI        = os.environ["MONGODB_URI"]
DATABASE_NAME      = os.getenv("DATABASE_NAME", "fastapi_db")
TEST_DATABASE_NAME = os.getenv("TEST_DATABASE_NAME", "fastapi_test_db")
 
MONGO_OPTIONS = {
    "maxPoolSize": 10,
    "serverSelectionTimeoutMS": 5000,
    "socketTimeoutMS": 30000,
}