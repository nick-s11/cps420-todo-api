from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from bson import ObjectId
from app.database.connection import database
from app.models.user import UserCreate, UserInDB, UserPublic, TokenResponse
from app.services.auth import (
    hash_password, verify_password, create_access_token, decode_access_token
)
 
router = APIRouter(prefix="/auth", tags=["auth"])
 
# Check FastAPI's interactive docs to the correct token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
 
 
# Helpers 
def get_users_collection():
    db = database.db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized")
    return db["users"]
 
 
async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserPublic:
    """Dependency: validate the Bearer token and return the current user.
    Raise 401 if the token is missing, expired, or tampered with.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = decode_access_token(token)
    if username is None:
        raise credentials_exception
 
    collection = get_users_collection()
    doc = await collection.find_one({"username": username})
    if doc is None:
        raise credentials_exception
 
    return UserPublic(id=str(doc['_id']), username=doc['username'])
 
 
# Endpoints 
@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Create a new user account. Passwords are hashed before storage."""
    collection = get_users_collection()
    existing = await collection.find_one({"username": user_data.username})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    hashed = hash_password(user_data.password)
    doc = {"username": user_data.username, "hashed_password": hashed}
    result = await collection.insert_one(doc)
    return UserPublic(id=str(result.inserted_id), username=user_data.username)
 
 
@router.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Exchange valid credentials for a JWT access token."""
    collection = get_users_collection()
    doc = await collection.find_one({"username": form_data.username})
    if not doc or not verify_password(form_data.password, doc['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(data={"sub": doc["username"]})
    return TokenResponse(access_token=token, token_type="bearer")