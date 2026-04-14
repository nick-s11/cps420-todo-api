import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
 
# Configuration 
# WARNING: change this in production! Store it in an environment variable.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
 
# bcrypt is the recommended hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
 
 
# Password helpers 
def hash_password(plain: str) -> str:
    """Return a bcrypt hash of a plain-text password."""
    return pwd_context.hash(plain)
 
 
def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored bcrypt hash."""
    return pwd_context.verify(plain, hashed)
 
 
# Token helpers 
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Encode data into a signed JWT. Include an exp claim."""
    payload = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
 
 
def decode_access_token(token: str) -> str | None:
    """Decode a JWT and return the username (sub claim), or None if invalid."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        return username
    except JWTError:
        return None