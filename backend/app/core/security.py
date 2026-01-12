"""
============================================
SAHAYAK AI - Security & Authentication
============================================

📌 WHAT IS THIS FILE?
Handles JWT token creation, verification, and password hashing.
We use simple JWT instead of Firebase for prototype simplicity.

🎓 LEARNING POINTS:
1. JWT (JSON Web Token): A compact token format for secure data transfer
2. Password Hashing: Never store plain passwords! bcrypt adds salt automatically
3. Bearer Token: The standard way to send tokens in HTTP headers

How JWT works:
1. User logs in with credentials
2. Server validates and creates a JWT with user info
3. Client stores JWT and sends it with each request
4. Server validates JWT and extracts user info
============================================
"""

from datetime import datetime, timedelta
from typing import Optional, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# --------------------------------------------
# Password Hashing Setup
# --------------------------------------------
# CryptContext handles password hashing using bcrypt
# bcrypt automatically adds a random "salt" to prevent rainbow table attacks

pwd_context = CryptContext(
    schemes=["bcrypt"],  # Use bcrypt algorithm
    deprecated="auto"     # Auto-handle deprecated schemes
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The password user entered
        hashed_password: The stored hashed password
    
    Returns:
        bool: True if passwords match, False otherwise
    
    🎓 LEARNING POINT:
    We never compare plain passwords directly.
    bcrypt re-hashes the plain password with the same salt
    and compares the results.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password to hash
    
    Returns:
        str: Hashed password (includes salt)
    
    🎓 LEARNING POINT:
    The hash includes the salt and algorithm info.
    Example: $2b$12$LQv3c1yqBW...
    - $2b$ = bcrypt version
    - $12$ = cost factor (number of iterations)
    - Rest = salt + hash
    """
    return pwd_context.hash(password)


# --------------------------------------------
# JWT Token Functions
# --------------------------------------------

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Payload data to encode in token (usually user_id, role)
        expires_delta: Optional custom expiration time
    
    Returns:
        str: Encoded JWT token
    
    🎓 LEARNING POINT:
    JWT has three parts: header.payload.signature
    - Header: Algorithm info
    - Payload: Your data + expiration time
    - Signature: Proves the token wasn't tampered with
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    # Add standard JWT claims
    to_encode.update({
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at
    })
    
    # Encode the token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: The JWT token string
    
    Returns:
        dict: Decoded payload if valid, None otherwise
    
    🎓 LEARNING POINT:
    Decoding validates:
    1. Signature matches (not tampered)
    2. Token not expired
    3. Algorithm matches expected
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        # Token invalid, expired, or tampered
        return None


def create_refresh_token(user_id: str) -> str:
    """
    Create a longer-lived refresh token.
    
    Args:
        user_id: The user's ID
    
    Returns:
        str: Refresh token (valid for 7 days)
    
    🎓 LEARNING POINT:
    Refresh tokens allow getting new access tokens
    without re-entering credentials. They have longer
    expiration but are only used once.
    """
    expires = timedelta(days=7)
    return create_access_token(
        data={"sub": user_id, "type": "refresh"},
        expires_delta=expires
    )
