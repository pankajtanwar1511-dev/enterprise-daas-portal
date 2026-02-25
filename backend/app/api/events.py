"""
Event Version Control API Endpoints
Provides event catalog, producer/consumer tracking, and compatibility management
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, List, Dict
from pydantic import BaseModel
from ..services.event_manager import EventManager
from ..database import get_db

router = APIRouter(prefix="/api/v1/events", tags=["Event Version Control"])


class EventRegister(BaseModel):
    event_name: str
    schema_definition: Dict
    schema_format: str = "JSON_SCHEMA"
    version: Optional[int] = None
    producer_asset_id: Optional[int] = None
    description: Optional[str] = None
    compatibility_mode: str = "BACKWARD"


class ConsumerRegister(BaseModel):
    consumer_asset_id: int
    version_constraint: Optional[str] = None


class BreakingChangeCheck(BaseModel):
    new_schema: Dict


class EventDeprecate(BaseModel):
    reason: str


@router.post("/register")
def register_event(
    request: EventRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new event or new version of existing event

    Args:
        request: Event registration details

    Returns:
        Registered event information

    Example:
        {
          "event_name": "customer.created",
          "schema_definition": {
            "type": "object",
            "properties": {
              "customer_id": {"type": "string"},
              "email": {"type": "string"}
            },
            "required": ["customer_id", "email"]
          },
          "producer_asset_id": 1,
          "description": "Customer creation event"
        }
    """
    try:
        manager = EventManager(db)
        result = manager.register_event(
            event_name=request.event_name,
            schema_definition=request.schema_definition,
            schema_format=request.schema_format,
            version=request.version,
            producer_asset_id=request.producer_asset_id,
            description=request.description,
            compatibility_mode=request.compatibility_mode
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event registration failed: {str(e)}")


@router.post("/{event_name}/consumers")
def register_consumer(
    event_name: str,
    request: ConsumerRegister,
    db: Session = Depends(get_db)
):
    """
    Register an asset as a consumer of an event

    Args:
        event_name: Event being consumed
        request: Consumer registration details

    Returns:
        Consumer registration information

    Example:
        POST /api/v1/events/customer.created/consumers
        {
          "consumer_asset_id": 5,
          "version_constraint": ">=1"
        }
    """
    try:
        manager = EventManager(db)
        result = manager.register_consumer(
            event_name=event_name,
            consumer_asset_id=request.consumer_asset_id,
            version_constraint=request.version_constraint
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consumer registration failed: {str(e)}")


@router.get("/catalog")
def get_event_catalog(
    search: Optional[str] = None,
    producer_asset_id: Optional[int] = None,
    active_only: bool = True,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get event catalog with search and filters

    Args:
        search: Search in event names and descriptions
        producer_asset_id: Filter by producer asset
        active_only: Only active events
        limit: Maximum events to return
        offset: Pagination offset

    Returns:
        Event catalog with metadata

    Example:
        GET /api/v1/events/catalog?search=customer&active_only=true
    """
    try:
        manager = EventManager(db)
        result = manager.get_event_catalog(
            search_query=search,
            producer_asset_id=producer_asset_id,
            active_only=active_only,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get event catalog: {str(e)}")


@router.get("/{event_name}/versions")
def get_event_versions(
    event_name: str,
    db: Session = Depends(get_db)
):
    """
    Get all versions of an event

    Args:
        event_name: Event to get versions for

    Returns:
        List of event versions with schemas

    Example:
        GET /api/v1/events/customer.created/versions
    """
    try:
        manager = EventManager(db)
        result = manager.get_event_versions(event_name)
        return {
            "event_name": event_name,
            "total_versions": len(result),
            "versions": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get versions: {str(e)}")


@router.get("/{event_name}/consumers")
def get_consumers(
    event_name: str,
    db: Session = Depends(get_db)
):
    """
    Get all consumers of an event

    Args:
        event_name: Event to get consumers for

    Returns:
        List of consumer assets

    Example:
        GET /api/v1/events/customer.created/consumers
    """
    try:
        manager = EventManager(db)
        result = manager.get_consumers(event_name)
        return {
            "event_name": event_name,
            "consumer_count": len(result),
            "consumers": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get consumers: {str(e)}")


@router.post("/{event_name}/check-breaking-changes")
def check_breaking_changes(
    event_name: str,
    request: BreakingChangeCheck,
    db: Session = Depends(get_db)
):
    """
    Check if new schema introduces breaking changes

    Args:
        event_name: Event to check
        request: New schema definition

    Returns:
        Breaking change analysis

    Example:
        POST /api/v1/events/customer.created/check-breaking-changes
        {
          "new_schema": {
            "type": "object",
            "properties": {
              "customer_id": {"type": "string"},
              "email": {"type": "string"},
              "phone": {"type": "string"}
            },
            "required": ["customer_id", "email", "phone"]
          }
        }
    """
    try:
        manager = EventManager(db)
        result = manager.check_breaking_changes(
            event_name=event_name,
            new_schema=request.new_schema
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Breaking change check failed: {str(e)}")


@router.get("/{event_name}/compatibility-matrix")
def get_compatibility_matrix(
    event_name: str,
    db: Session = Depends(get_db)
):
    """
    Get version compatibility matrix for an event

    Args:
        event_name: Event to analyze

    Returns:
        Compatibility matrix showing which versions are compatible

    Example:
        GET /api/v1/events/customer.created/compatibility-matrix
    """
    try:
        manager = EventManager(db)
        result = manager.get_compatibility_matrix(event_name)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get compatibility matrix: {str(e)}")


@router.patch("/{event_name}/versions/{version}/deprecate")
def deprecate_event_version(
    event_name: str,
    version: int,
    request: EventDeprecate,
    db: Session = Depends(get_db)
):
    """
    Deprecate a specific event version

    Args:
        event_name: Event name
        version: Version to deprecate
        request: Deprecation reason

    Returns:
        Deprecation information

    Example:
        PATCH /api/v1/events/customer.created/versions/1/deprecate
        {
          "reason": "Schema incompatibility - use version 2"
        }
    """
    try:
        manager = EventManager(db)
        result = manager.deprecate_event_version(
            event_name=event_name,
            version=version,
            reason=request.reason
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deprecation failed: {str(e)}")


@router.get("/statistics")
def get_event_statistics(db: Session = Depends(get_db)):
    """
    Get overall event catalog statistics

    Returns:
        Event catalog statistics
    """
    from .. import models_advanced

    total_events = db.query(models_advanced.SchemaRegistry).filter(
        models_advanced.SchemaRegistry.is_latest == True
    ).count()

    active_events = db.query(models_advanced.SchemaRegistry).filter(
        and_(
            models_advanced.SchemaRegistry.is_latest == True,
            models_advanced.SchemaRegistry.is_active == True
        )
    ).count()

    deprecated_events = total_events - active_events

    # Total versions
    total_versions = db.query(models_advanced.SchemaRegistry).count()

    # Format breakdown
    format_counts = db.query(
        models_advanced.SchemaRegistry.schema_format,
        func.count(models_advanced.SchemaRegistry.schema_id)
    ).filter(
        models_advanced.SchemaRegistry.is_latest == True
    ).group_by(
        models_advanced.SchemaRegistry.schema_format
    ).all()

    return {
        "total_events": total_events,
        "active_events": active_events,
        "deprecated_events": deprecated_events,
        "total_versions": total_versions,
        "avg_versions_per_event": round(total_versions / total_events, 2) if total_events > 0 else 0,
        "events_by_format": {
            fmt.value: count for fmt, count in format_counts
        }
    }
