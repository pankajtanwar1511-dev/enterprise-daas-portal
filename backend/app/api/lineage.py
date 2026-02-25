"""
Data Lineage API Endpoints
Provides lineage tracking, SQL parsing, and visualization capabilities
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from pydantic import BaseModel
from ..services.lineage_tracker import LineageTracker
from ..database import get_db

router = APIRouter(prefix="/api/v1/lineage", tags=["Data Lineage"])


class LineageEdgeCreate(BaseModel):
    source_asset_id: int
    target_asset_id: int
    transformation_type: str  # SELECT, JOIN, AGGREGATE, UNION, FILTER
    transformation_logic: Optional[str] = None
    column_mappings: Optional[Dict] = None
    metadata: Optional[Dict] = None


class SQLLineageRequest(BaseModel):
    sql_query: str
    target_asset_id: int
    database_mapping: Optional[Dict[str, int]] = None


class BulkLineageImport(BaseModel):
    lineage_data: List[Dict]


@router.post("/register")
def register_lineage_edge(
    request: LineageEdgeCreate,
    db: Session = Depends(get_db)
):
    """
    Manually register a lineage relationship between two assets

    Args:
        request: Lineage edge definition

    Returns:
        Created lineage edge information
    """
    try:
        tracker = LineageTracker(db)
        result = tracker.register_lineage(
            source_asset_id=request.source_asset_id,
            target_asset_id=request.target_asset_id,
            transformation_type=request.transformation_type,
            transformation_logic=request.transformation_logic,
            column_mappings=request.column_mappings,
            metadata=request.metadata
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lineage registration failed: {str(e)}")


@router.post("/parse-sql")
def parse_sql_lineage(
    request: SQLLineageRequest,
    db: Session = Depends(get_db)
):
    """
    Parse SQL query to automatically extract lineage relationships

    Args:
        request: SQL query and target asset information

    Returns:
        Extracted lineage information with source tables and transformations
    """
    try:
        tracker = LineageTracker(db)
        result = tracker.parse_sql_lineage(
            sql_query=request.sql_query,
            target_asset_id=request.target_asset_id,
            database_mapping=request.database_mapping
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SQL parsing failed: {str(e)}")


@router.get("/path/{asset_id}")
def get_lineage_path(
    asset_id: int,
    direction: str = "both",  # upstream, downstream, or both
    max_depth: int = 5,
    db: Session = Depends(get_db)
):
    """
    Get complete lineage path for an asset

    Args:
        asset_id: Asset ID to trace
        direction: Direction to traverse ("upstream", "downstream", or "both")
        max_depth: Maximum depth to traverse

    Returns:
        Complete lineage path with upstream and downstream dependencies
    """
    if direction not in ["upstream", "downstream", "both"]:
        raise HTTPException(
            status_code=400,
            detail="Direction must be 'upstream', 'downstream', or 'both'"
        )

    try:
        tracker = LineageTracker(db)
        result = tracker.get_lineage_path(
            asset_id=asset_id,
            direction=direction,
            max_depth=max_depth
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lineage path retrieval failed: {str(e)}")


@router.post("/verify/{edge_id}")
def verify_lineage_edge(
    edge_id: int,
    db: Session = Depends(get_db)
):
    """
    Verify that a lineage edge is still valid

    Args:
        edge_id: Edge ID to verify

    Returns:
        Verification status
    """
    try:
        tracker = LineageTracker(db)
        result = tracker.verify_lineage(edge_id=edge_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lineage verification failed: {str(e)}")


@router.post("/bulk-import")
def bulk_import_lineage(
    request: BulkLineageImport,
    db: Session = Depends(get_db)
):
    """
    Bulk import lineage relationships from external system

    Args:
        request: List of lineage edge definitions

    Returns:
        Import statistics (created, updated, failed counts)
    """
    try:
        tracker = LineageTracker(db)
        result = tracker.bulk_import_lineage(
            lineage_data=request.lineage_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk import failed: {str(e)}")


@router.get("/nodes")
def list_lineage_nodes(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List all lineage nodes

    Args:
        limit: Maximum number of nodes to return
        offset: Offset for pagination

    Returns:
        List of lineage nodes with basic information
    """
    from .. import models_advanced

    nodes = db.query(models_advanced.DataLineageNode).limit(limit).offset(offset).all()

    return {
        "count": len(nodes),
        "nodes": [{
            "node_id": n.node_id,
            "asset_id": n.asset_id,
            "node_type": n.node_type.value,
            "node_name": n.node_name,
            "location": n.location,
            "created_at": n.created_at.isoformat()
        } for n in nodes]
    }


@router.get("/edges")
def list_lineage_edges(
    active_only: bool = True,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List all lineage edges

    Args:
        active_only: Only return active edges
        limit: Maximum number of edges to return
        offset: Offset for pagination

    Returns:
        List of lineage edges with transformation information
    """
    from .. import models_advanced

    query = db.query(models_advanced.DataLineageEdge)

    if active_only:
        query = query.filter(models_advanced.DataLineageEdge.is_active == True)

    edges = query.limit(limit).offset(offset).all()

    return {
        "count": len(edges),
        "edges": [{
            "edge_id": e.edge_id,
            "source_node_id": e.source_node_id,
            "target_node_id": e.target_node_id,
            "transformation_type": e.transformation_type.value,
            "is_active": e.is_active,
            "discovered_at": e.discovered_at.isoformat(),
            "last_verified_at": e.last_verified_at.isoformat() if e.last_verified_at else None
        } for e in edges]
    }


@router.get("/statistics")
def get_lineage_statistics(db: Session = Depends(get_db)):
    """
    Get lineage statistics

    Returns:
        Statistics about lineage nodes, edges, and coverage
    """
    from .. import models, models_advanced

    total_assets = db.query(models.Asset).count()
    total_nodes = db.query(models_advanced.DataLineageNode).count()
    total_edges = db.query(models_advanced.DataLineageEdge).filter(
        models_advanced.DataLineageEdge.is_active == True
    ).count()

    # Count edges by transformation type
    edge_types = db.query(
        models_advanced.DataLineageEdge.transformation_type,
        db.func.count(models_advanced.DataLineageEdge.edge_id)
    ).filter(
        models_advanced.DataLineageEdge.is_active == True
    ).group_by(
        models_advanced.DataLineageEdge.transformation_type
    ).all()

    coverage = (total_nodes / total_assets * 100) if total_assets > 0 else 0

    return {
        "total_assets": total_assets,
        "total_lineage_nodes": total_nodes,
        "total_lineage_edges": total_edges,
        "lineage_coverage_percent": round(coverage, 2),
        "edges_by_type": {
            edge_type.value: count for edge_type, count in edge_types
        }
    }
