"""
============================================
SAHAYAK AI - Authentication Endpoints
============================================

📌 WHAT IS THIS FILE?
API endpoints for user registration, login, and profile.
Uses simple JWT authentication (no Firebase).

🎓 LEARNING POINT:
- POST endpoints receive data in request body
- Response models define what data is returned
- Dependencies (Depends) inject authentication
============================================
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends

from app.schemas.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    Message
)
from app.db.models.user import User, UserRole
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token
)
from app.core.dependencies import get_current_active_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user.
    
    Creates a new user account and returns an access token.
    
    - **email**: User's email address (must be unique)
    - **password**: Password (min 6 characters)
    - **name**: Full name
    - **role**: teacher, crp, or diet
    """
    # Check if email already exists
    existing_user = await User.find_one(User.email == user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role
    try:
        role = UserRole(user_data.role.lower())
    except ValueError:
        role = UserRole.TEACHER
    
    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password),
        role=role,
        school_id=user_data.school_id,
        school_name=user_data.school_name,
        district=user_data.district,
        phone=user_data.phone,
        subjects=user_data.subjects,
        grades=user_data.grades,
        preferred_language=user_data.preferred_language,
    )
    
    await user.insert()
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role.value,
            school_id=user.school_id,
            school_name=user.school_name,
            district=user.district,
            subjects=user.subjects,
            grades=user.grades,
            preferred_language=user.preferred_language,
            is_active=user.is_active,
            created_at=user.created_at,
            total_sos_requests=user.total_sos_requests,
        )
    )


@router.post("/login", response_model=TokenResponse)
async def login(login_data: UserLogin):
    """
    Login with email and password.
    
    Returns an access token if credentials are valid.
    """
    # Find user by email
    user = await User.find_one(User.email == login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is disabled"
        )
    
    # Update last login
    user.update_login()
    await user.save()
    
    # Create access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user=UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            role=user.role.value,
            school_id=user.school_id,
            school_name=user.school_name,
            district=user.district,
            subjects=user.subjects,
            grades=user.grades,
            preferred_language=user.preferred_language,
            is_active=user.is_active,
            created_at=user.created_at,
            total_sos_requests=user.total_sos_requests,
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user's profile.
    
    Requires a valid JWT token in the Authorization header.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        school_id=current_user.school_id,
        school_name=current_user.school_name,
        district=current_user.district,
        subjects=current_user.subjects,
        grades=current_user.grades,
        preferred_language=current_user.preferred_language,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        total_sos_requests=current_user.total_sos_requests,
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    update_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user's profile.
    
    Allowed fields: name, school_id, school_name, district,
    phone, subjects, grades, preferred_language
    """
    allowed_fields = [
        "name", "school_id", "school_name", "district",
        "phone", "subjects", "grades", "preferred_language"
    ]
    
    for field, value in update_data.items():
        if field in allowed_fields:
            setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    await current_user.save()
    
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        school_id=current_user.school_id,
        school_name=current_user.school_name,
        district=current_user.district,
        subjects=current_user.subjects,
        grades=current_user.grades,
        preferred_language=current_user.preferred_language,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        total_sos_requests=current_user.total_sos_requests,
    )
