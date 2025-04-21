
from datetime import datetime, timedelta 
from jose import JWTError, jwt           

# -----------------
# JWT Configuration

# Secret key to sign the JWT token 
SECRET_KEY = "mysecretkey"

# Algorithm used for signing and verifying the token
ALGORITHM = "HS256"

# Default token expiry time (30 minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# -----------------
# Token Creation Function

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Creates a signed JWT token using provided user data.
    
    Parameters:
        - data (dict): Data to include in the token (typically user ID)
        - expires_delta (timedelta | None): Optional custom expiry time
    
    Returns:
        - str: Encoded JWT token
    """
    to_encode = data.copy()  
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# -----------------
# Token Verification Function

def verify_token(token: str):
    """
    Verifies the JWT token sent by client and returns the decoded payload.
    
    Parameters:
        - token (str): The JWT token passed in Authorization header
    
    Returns:
        - dict: Decoded payload if token is valid
        - None: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Decode and verify token
        return payload
    except JWTError:
        return None  # Invalid signature or token is expired
