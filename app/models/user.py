from typing import Optional
from pydantic import BaseModel, Field
 
 
class UserCreate(BaseModel):
    """Shape of data when registering a new user."""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
 
 
class UserInDB(BaseModel):
    """What a user looks like stored in MongoDB (password is always hashed)."""
    id: Optional[str] = None
    username: str
    hashed_password: str
 
 
class UserPublic(BaseModel):
    """Safe version returned to callers — never includes the password hash."""
    id: Optional[str] = None
    username: str
 
 
class TokenResponse(BaseModel):
    """JWT token response returned by POST /auth/token."""
    access_token: str
    token_type: str = "bearer"