"""
API Key Management API
Allows users to create and manage API keys for programmatic access
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
import secrets
import hashlib

from ..database import get_db
from ..dependencies import get_current_user
from .. import models
from ..models_integrations import APIKey
from ..schemas_integrations import (
    APIKeyCreate,
    APIKeyResponse,
    APIKeyCreatedResponse
)

router = APIRouter(prefix="/api/v1/api-keys", tags=["API Keys"])


def generate_api_key() -> tuple[str, str, str]:
    """
    Generate a secure API key.
    Returns: (full_key, key_prefix, key_hash)

    Format: gp_<random_40_chars>
    """
    random_part = secrets.token_urlsafe(30)  # ~40 chars when base64 encoded
    full_key = f"gp_{random_part}"

    # Prefix for display (first 10 chars)
    key_prefix = full_key[:10]

    # Hash for storage
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()

    return full_key, key_prefix, key_hash


@router.post("/", response_model=APIKeyCreatedResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new API key for programmatic access.

    **Important:** The full API key is only shown once during creation.
    Save it immediately - you won't be able to retrieve it later.
    """
    # Generate API key
    full_key, key_prefix, key_hash = generate_api_key()

    # Calculate expiration if specified
    expires_at = None
    if key_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)

    # Create API key record
    api_key = APIKey(
        user_id=current_user.user_id,
        key_name=key_data.key_name,
        key_prefix=key_prefix,
        key_hash=key_hash,
        scopes=key_data.scopes or [],
        expires_at=expires_at,
        rate_limit_per_hour=key_data.rate_limit_per_hour,
        active=True
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return APIKeyCreatedResponse(
        key_id=api_key.key_id,
        key_name=api_key.key_name,
        api_key=full_key,
        key_prefix=key_prefix,
        scopes=api_key.scopes,
        created_at=api_key.created_at,
        expires_at=api_key.expires_at
    )


@router.get("/", response_model=List[APIKeyResponse])
async def list_api_keys(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """List all API keys for the current user"""
    query = db.query(APIKey).filter(APIKey.user_id == current_user.user_id)

    if active_only:
        query = query.filter(APIKey.active == True)
        # Also filter out expired keys
        query = query.filter(
            (APIKey.expires_at.is_(None)) | (APIKey.expires_at > datetime.utcnow())
        )

    keys = query.offset(skip).limit(limit).all()
    return keys


@router.get("/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get API key details by ID"""
    api_key = db.query(APIKey).filter(
        APIKey.key_id == key_id,
        APIKey.user_id == current_user.user_id
    ).first()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    return api_key


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def revoke_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Revoke (delete) an API key"""
    api_key = db.query(APIKey).filter(
        APIKey.key_id == key_id,
        APIKey.user_id == current_user.user_id
    ).first()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    db.delete(api_key)
    db.commit()
    return None


@router.patch("/{key_id}/deactivate", response_model=APIKeyResponse)
async def deactivate_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Deactivate an API key without deleting it"""
    api_key = db.query(APIKey).filter(
        APIKey.key_id == key_id,
        APIKey.user_id == current_user.user_id
    ).first()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    api_key.active = False
    db.commit()
    db.refresh(api_key)

    return api_key


@router.patch("/{key_id}/activate", response_model=APIKeyResponse)
async def activate_api_key(
    key_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Reactivate a deactivated API key"""
    api_key = db.query(APIKey).filter(
        APIKey.key_id == key_id,
        APIKey.user_id == current_user.user_id
    ).first()

    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    # Check if key has expired
    if api_key.expires_at and api_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="Cannot activate expired API key"
        )

    api_key.active = True
    db.commit()
    db.refresh(api_key)

    return api_key


# Helper function to validate API key (to be used in dependencies)
async def validate_api_key(
    api_key: str,
    db: Session
) -> models.User:
    """
    Validate API key and return associated user.
    Raises HTTPException if invalid.
    """
    # Hash the provided key
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Find key in database
    db_key = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()

    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    # Check if key is active
    if not db_key.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has been deactivated"
        )

    # Check if key has expired
    if db_key.expires_at and db_key.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key has expired"
        )

    # Update usage stats
    db_key.last_used_at = datetime.utcnow()
    db_key.usage_count += 1
    db.commit()

    # Get and return user
    user = db.query(models.User).filter(models.User.user_id == db_key.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user
