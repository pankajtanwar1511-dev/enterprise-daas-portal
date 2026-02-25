"""
Schema Registry API Endpoints
Provides schema versioning, compatibility checking, and validation
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel
from ..services.schema_registry import SchemaRegistry
from ..database import get_db

router = APIRouter(prefix="/api/v1/schemas", tags=["Schema Registry"])


class SchemaRegister(BaseModel):
    subject: str
    schema_format: str  # AVRO, JSON_SCHEMA, PROTOBUF
    schema_definition: Dict
    compatibility_mode: str = "BACKWARD"  # BACKWARD, FORWARD, FULL, NONE
    asset_id: Optional[int] = None
    description: Optional[str] = None


class CompatibilityCheck(BaseModel):
    new_schema: Dict


class DataValidation(BaseModel):
    data: Dict


@router.post("/register")
def register_schema(
    request: SchemaRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new schema or new version of existing schema

    Args:
        request: Schema registration details

    Returns:
        Registered schema information with version number
    """
    try:
        registry = SchemaRegistry(db)
        result = registry.register_schema(
            subject=request.subject,
            schema_format=request.schema_format,
            schema_definition=request.schema_definition,
            compatibility_mode=request.compatibility_mode,
            asset_id=request.asset_id,
            description=request.description
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema registration failed: {str(e)}")


@router.get("/subjects")
def list_subjects(db: Session = Depends(get_db)):
    """
    List all schema subjects

    Returns:
        List of unique schema subjects
    """
    try:
        registry = SchemaRegistry(db)
        subjects = registry.list_subjects()
        return {"subjects": subjects, "count": len(subjects)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list subjects: {str(e)}")


@router.get("/subjects/{subject}/versions")
def list_versions(subject: str, db: Session = Depends(get_db)):
    """
    List all versions for a subject

    Args:
        subject: Schema subject

    Returns:
        List of version numbers
    """
    try:
        registry = SchemaRegistry(db)
        versions = registry.list_versions(subject)
        return {"subject": subject, "versions": versions, "count": len(versions)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list versions: {str(e)}")


@router.get("/subjects/{subject}/versions/{version}")
def get_schema_version(
    subject: str,
    version: int,
    db: Session = Depends(get_db)
):
    """
    Get specific version of a schema

    Args:
        subject: Schema subject
        version: Version number

    Returns:
        Complete schema information including definition
    """
    try:
        registry = SchemaRegistry(db)
        schema = registry.get_schema(subject, version)
        return schema
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")


@router.get("/subjects/{subject}/versions/latest")
def get_latest_schema(
    subject: str,
    db: Session = Depends(get_db)
):
    """
    Get latest version of a schema

    Args:
        subject: Schema subject

    Returns:
        Latest schema information including definition
    """
    try:
        registry = SchemaRegistry(db)
        schema = registry.get_schema(subject, version=None)
        return schema
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")


@router.post("/compatibility/{subject}")
def check_compatibility(
    subject: str,
    request: CompatibilityCheck,
    version: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Check if a new schema is compatible with existing version

    Args:
        subject: Schema subject
        request: New schema to check
        version: Version to check against (if None, checks latest)

    Returns:
        Compatibility status with detailed errors if incompatible
    """
    try:
        registry = SchemaRegistry(db)
        result = registry.check_compatibility(
            subject=subject,
            new_schema=request.new_schema,
            version=version
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compatibility check failed: {str(e)}")


@router.get("/compare/{subject}")
def compare_schemas(
    subject: str,
    version1: int,
    version2: int,
    db: Session = Depends(get_db)
):
    """
    Compare two schema versions and identify differences

    Args:
        subject: Schema subject
        version1: First version
        version2: Second version

    Returns:
        Detailed differences between the two versions
    """
    try:
        registry = SchemaRegistry(db)
        result = registry.compare_schemas(
            subject=subject,
            version1=version1,
            version2=version2
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema comparison failed: {str(e)}")


@router.post("/validate/{subject}")
def validate_data(
    subject: str,
    request: DataValidation,
    version: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Validate data against a schema

    Args:
        subject: Schema subject
        request: Data to validate
        version: Schema version (if None, uses latest)

    Returns:
        Validation result with detailed errors if invalid
    """
    try:
        registry = SchemaRegistry(db)
        result = registry.validate_data_against_schema(
            subject=subject,
            data=request.data,
            version=version
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data validation failed: {str(e)}")


@router.get("/statistics")
def get_schema_statistics(db: Session = Depends(get_db)):
    """
    Get schema registry statistics

    Returns:
        Statistics about registered schemas and versions
    """
    from .. import models_advanced

    total_subjects = db.query(models_advanced.SchemaRegistry.subject).distinct().count()
    total_versions = db.query(models_advanced.SchemaRegistry).count()

    # Count by format
    format_counts = db.query(
        models_advanced.SchemaRegistry.schema_format,
        db.func.count(models_advanced.SchemaRegistry.schema_id)
    ).group_by(
        models_advanced.SchemaRegistry.schema_format
    ).all()

    # Count by compatibility mode
    compatibility_counts = db.query(
        models_advanced.SchemaRegistry.compatibility_mode,
        db.func.count(models_advanced.SchemaRegistry.schema_id)
    ).group_by(
        models_advanced.SchemaRegistry.compatibility_mode
    ).all()

    return {
        "total_subjects": total_subjects,
        "total_versions": total_versions,
        "average_versions_per_subject": round(total_versions / total_subjects, 2) if total_subjects > 0 else 0,
        "schemas_by_format": {
            fmt.value: count for fmt, count in format_counts
        },
        "schemas_by_compatibility": {
            compat.value: count for compat, count in compatibility_counts
        }
    }
