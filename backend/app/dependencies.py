"""
Dependency functions for FastAPI endpoints
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional
from .database import get_db
from . import models
from .auth import decode_access_token

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    """
    Get the current authenticated user from JWT token.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        User: Current authenticated user

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Get username from token
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise credentials_exception

    # Query user from database
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_active_admin(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Verify that the current user has admin role.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current user if admin

    Raises:
        HTTPException: If user is not an admin
    """
    if current_user.role.role_name != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_active_data_steward(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """
    Verify that the current user is either admin or data steward.

    Args:
        current_user: Current authenticated user

    Returns:
        User: Current user if admin or data steward

    Raises:
        HTTPException: If user is neither admin nor data steward
    """
    allowed_roles = ["Admin", "DataSteward"]
    if current_user.role.role_name not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Data Steward access required"
        )
    return current_user
