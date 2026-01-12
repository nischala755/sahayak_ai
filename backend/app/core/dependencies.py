"""
============================================
SAHAYAK AI - FastAPI Dependencies
============================================

📌 WHAT IS THIS FILE?
FastAPI dependencies are reusable functions that run before
your route handlers. They're perfect for:
- Authentication checks
- Database session management
- Permission validation

🎓 LEARNING POINT:
Dependency Injection is a design pattern where:
1. You define what a function needs (dependencies)
2. FastAPI automatically provides those dependencies
3. This makes code modular and testable
============================================
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.security import decode_access_token
from app.db.mongodb import get_database
from app.db.models.user import User

# --------------------------------------------
# Security Scheme
# --------------------------------------------
# HTTPBearer expects: Authorization: Bearer <token>
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Extract and validate the current user from JWT token.
    
    This is a dependency - FastAPI calls it automatically when you add:
    current_user: User = Depends(get_current_user)
    
    Args:
        credentials: Automatically extracted from Authorization header
    
    Returns:
        User: The authenticated user object
    
    Raises:
        HTTPException: If token is invalid or user not found
    
    🎓 LEARNING POINT:
    The Depends() function tells FastAPI:
    "Before running this route, first run get_current_user
     and pass its result as 'credentials'"
    """
    # Decode the JWT token
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user ID from token
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = await User.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Ensure the current user is active (not disabled).
    
    This chains dependencies - it first calls get_current_user,
    then checks if the user is active.
    
    Returns:
        User: The authenticated and active user
    
    Raises:
        HTTPException: If user is disabled
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def require_role(required_roles: list):
    """
    Create a dependency that checks user role.
    
    Usage:
        @router.get("/admin", dependencies=[Depends(require_role(["admin", "diet"]))])
    
    Args:
        required_roles: List of roles that can access the endpoint
    
    Returns:
        Dependency function that validates role
    
    🎓 LEARNING POINT:
    This is a dependency factory - a function that returns
    a dependency. It allows parameterized dependencies.
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {required_roles}"
            )
        return current_user
    
    return role_checker


# Convenience dependencies for common roles
require_teacher = require_role(["teacher", "crp", "diet"])
require_crp = require_role(["crp", "diet"])
require_diet = require_role(["diet"])


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[User]:
    """
    Optionally get the current user (for public endpoints).
    
    Unlike get_current_user, this doesn't raise an error
    if no token is provided. Useful for endpoints that
    behave differently for logged-in vs anonymous users.
    
    Returns:
        User or None: The user if authenticated, None otherwise
    """
    if credentials is None:
        return None
    
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        return None
    
    user_id = payload.get("sub")
    if user_id is None:
        return None
    
    return await User.get(user_id)
