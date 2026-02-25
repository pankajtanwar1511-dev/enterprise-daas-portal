"""
Impact Analysis API Endpoints
Provides impact analysis and dependency visualization capabilities
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from ..services.impact_analyzer import ImpactAnalyzer
from ..database import get_db

router = APIRouter(prefix="/api/v1/impact", tags=["Impact Analysis"])


class ImpactAnalysisRequest(BaseModel):
    change_type: str  # schema_change, deprecation, deletion, policy_change, metadata_update
    change_description: Optional[str] = ""
    analysis_depth: Optional[int] = 5


@router.post("/analyze/{asset_id}")
def analyze_asset_impact(
    asset_id: int,
    request: ImpactAnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Perform comprehensive impact analysis for a proposed asset change

    Args:
        asset_id: ID of the asset being changed
        request: Change details including type, description, and analysis depth

    Returns:
        Complete impact analysis including:
        - Impact score (LOW, MEDIUM, HIGH, CRITICAL)
        - Upstream and downstream dependencies
        - Affected stakeholders
        - Migration effort estimate
        - Recommended actions
    """
    try:
        analyzer = ImpactAnalyzer(db)
        result = analyzer.analyze_asset_change(
            asset_id=asset_id,
            change_type=request.change_type,
            change_description=request.change_description,
            analysis_depth=request.analysis_depth
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impact analysis failed: {str(e)}")


@router.get("/visualization/{asset_id}")
def get_dependency_graph(
    asset_id: int,
    db: Session = Depends(get_db)
):
    """
    Get dependency graph visualization data for an asset

    Args:
        asset_id: ID of the asset to visualize

    Returns:
        Graph data with nodes and edges suitable for D3.js or React Flow:
        - nodes: List of asset nodes with metadata
        - edges: List of dependency edges with transformation info
        - central_asset_id: The asset being visualized
    """
    try:
        analyzer = ImpactAnalyzer(db)
        result = analyzer.get_dependency_graph_visualization(asset_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization generation failed: {str(e)}")


@router.get("/history/{asset_id}")
def get_impact_analysis_history(
    asset_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get historical impact analysis results for an asset

    Args:
        asset_id: ID of the asset
        limit: Maximum number of results to return

    Returns:
        List of historical impact analysis runs
    """
    from .. import models_advanced

    analyses = db.query(models_advanced.ImpactAnalysisRun).filter(
        models_advanced.ImpactAnalysisRun.asset_id == asset_id
    ).order_by(
        models_advanced.ImpactAnalysisRun.analyzed_at.desc()
    ).limit(limit).all()

    return [{
        "analysis_id": a.analysis_id,
        "change_type": a.change_type,
        "impact_score": a.impact_score,
        "downstream_dependencies_count": a.downstream_dependencies_count,
        "affected_users_count": a.affected_users_count,
        "migration_required": a.migration_required,
        "estimated_migration_hours": a.estimated_migration_hours,
        "analyzed_at": a.analyzed_at.isoformat()
    } for a in analyses]
