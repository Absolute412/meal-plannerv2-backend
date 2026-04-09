from src.utils.config import settings
from datetime import datetime, timedelta
from jose import jwt

# Secrete key should be long and random in production
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict):
    """Create a JWT token with user info in 'sub' """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})   # exp - expiry time
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # signs the token with secret key
    return token
