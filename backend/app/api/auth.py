"""Authentication routes."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# Request/Response Models
class UserCreate(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str
    name: str


class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    name: str
    created_at: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""
    user_id: str | None = None


# Routes
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """
    Register a new user.
    
    - **email**: User's email address
    - **password**: User's password (min 8 characters)
    - **name**: User's display name
    """
    # TODO: Implement with database
    # 1. Check if email exists
    # 2. Hash password
    # 3. Create user in DB
    # 4. Return user
    
    return UserResponse(
        id="placeholder-uuid",
        email=user_data.email,
        name=user_data.name,
        created_at="2025-01-01T00:00:00Z"
    )


@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Authenticate user and return JWT token.
    
    Use OAuth2 password flow with username (email) and password.
    """
    # TODO: Implement with database
    # 1. Find user by email
    # 2. Verify password
    # 3. Generate JWT token
    # 4. Return token
    
    return Token(
        access_token="placeholder-jwt-token",
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Get current authenticated user.
    
    Requires valid JWT token in Authorization header.
    """
    # TODO: Implement token validation
    # 1. Decode JWT token
    # 2. Get user from DB
    # 3. Return user
    
    return UserResponse(
        id="placeholder-uuid",
        email="user@example.com",
        name="Demo User",
        created_at="2025-01-01T00:00:00Z"
    )


@router.post("/logout")
async def logout(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Logout user (invalidate token).
    
    Note: With JWT, true logout requires token blocklist.
    """
    # TODO: Add token to blocklist if implementing server-side logout
    return {"message": "Successfully logged out"}
