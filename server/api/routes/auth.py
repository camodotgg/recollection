"""Authentication routes for user registration and login."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from server.db.database import get_db
from server.db.models import UserDB
from server.schemas.auth import UserRegister, UserLogin, TokenResponse, RefreshTokenRequest, UserResponse
from server.security.jwt import hash_password, verify_password, create_access_token, create_refresh_token, verify_token
from server.api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    session: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Register a new user.

    Args:
        user_data: User registration data (email, password)
        session: Database session

    Returns:
        TokenResponse with access and refresh tokens

    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    result = await session.execute(select(UserDB).where(UserDB.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    hashed_pw = hash_password(user_data.password)
    new_user = UserDB(
        email=user_data.email,
        hashed_password=hashed_pw,
        is_active=True
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # Create tokens
    access_token = create_access_token(data={"sub": new_user.id})
    refresh_token = create_refresh_token(data={"sub": new_user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    session: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Login an existing user.

    Args:
        login_data: User login data (email, password)
        session: Database session

    Returns:
        TokenResponse with access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    result = await session.execute(select(UserDB).where(UserDB.email == login_data.email))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    refresh_data: RefreshTokenRequest,
    session: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """
    Refresh access token using refresh token.

    Args:
        refresh_data: Refresh token
        session: Database session

    Returns:
        TokenResponse with new access and refresh tokens

    Raises:
        HTTPException: If refresh token is invalid
    """
    # Verify refresh token
    user_id = verify_token(refresh_data.refresh_token, token_type="refresh")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    result = await session.execute(select(UserDB).where(UserDB.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    access_token = create_access_token(data={"sub": user.id})
    new_refresh_token = create_refresh_token(data={"sub": user.id})

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserDB = Depends(get_current_user)
) -> UserResponse:
    """
    Get current authenticated user information.

    Args:
        current_user: Current authenticated user from dependency

    Returns:
        UserResponse with user information
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )
