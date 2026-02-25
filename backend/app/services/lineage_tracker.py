"""
Data Lineage Tracking Engine
Tracks data flow from source to destination with transformations
Supports SQL parsing for automated lineage extraction
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re
from .. import models, models_advanced


class LineageTracker:
    """
    Tracks and manages data lineage across the data ecosystem
    Supports manual registration and automated SQL parsing
    """

    def __init__(self, db: Session):
        self.db = db

    def register_lineage(
        self,
        source_asset_id: int,
        target_asset_id: int,
        transformation_type: str,
        transformation_logic: Optional[str] = None,
        column_mappings: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Manually register a lineage relationship between two assets

        Args:
            source_asset_id: Source asset ID
            target_asset_id: Target asset ID
            transformation_type: Type (SELECT, JOIN, AGGREGATE, UNION, etc.)
            transformation_logic: SQL query or script
            column_mappings: Dict mapping source columns to target columns
            metadata: Additional metadata

        Returns:
            Dict with created lineage information
        """
        # Validate assets exist
        source_asset = self.db.query(models.Asset).filter(
            models.Asset.asset_id == source_asset_id
        ).first()
        target_asset = self.db.query(models.Asset).filter(
            models.Asset.asset_id == target_asset_id
        ).first()

        if not source_asset or not target_asset:
            raise ValueError("Source or target asset not found")

        # Create or get lineage nodes
        source_node = self._get_or_create_node(source_asset)
        target_node = self._get_or_create_node(target_asset)

        # Check if edge already exists
        existing_edge = self.db.query(models_advanced.DataLineageEdge).filter(
            and_(
                models_advanced.DataLineageEdge.source_node_id == source_node.node_id,
                models_advanced.DataLineageEdge.target_node_id == target_node.node_id,
                models_advanced.DataLineageEdge.is_active == True
            )
        ).first()

        if existing_edge:
            # Update existing edge
            existing_edge.transformation_type = models_advanced.TransformationType[transformation_type]
            existing_edge.transformation_logic = transformation_logic
            existing_edge.column_mappings = column_mappings
            existing_edge.metadata = metadata
            existing_edge.last_verified_at = datetime.utcnow()
            edge = existing_edge
        else:
            # Create new edge
            edge = models_advanced.DataLineageEdge(
                source_node_id=source_node.node_id,
                target_node_id=target_node.node_id,
                transformation_type=models_advanced.TransformationType[transformation_type],
                transformation_logic=transformation_logic,
                column_mappings=column_mappings or {},
                is_active=True,
                metadata=metadata or {},
                discovered_at=datetime.utcnow(),
                last_verified_at=datetime.utcnow()
            )
            self.db.add(edge)

        self.db.commit()

        return {
            "edge_id": edge.edge_id,
            "source_asset": source_asset.asset_name,
            "target_asset": target_asset.asset_name,
            "transformation_type": transformation_type,
            "created_at": edge.discovered_at.isoformat()
        }

    def parse_sql_lineage(
        self,
        sql_query: str,
        target_asset_id: int,
        database_mapping: Optional[Dict[str, int]] = None
    ) -> Dict:
        """
        Parse SQL query to extract lineage relationships automatically

        Args:
            sql_query: SQL query to parse
            target_asset_id: Target asset being created/updated by this query
            database_mapping: Map of table names to asset IDs

        Returns:
            Dict with extracted lineage information
        """
        # Basic SQL parsing (production would use sqlparse or sqlglot library)
        lineage_edges = []

        # Extract source tables from FROM and JOIN clauses
        source_tables = self._extract_source_tables(sql_query)

        # Detect transformation type
        transformation_type = self._detect_transformation_type(sql_query)

        # Extract column mappings
        column_mappings = self._extract_column_mappings(sql_query, source_tables)

        # Create lineage edges for each source table
        for table_name in source_tables:
            # Try to find asset by name or use provided mapping
            source_asset_id = None

            if database_mapping and table_name in database_mapping:
                source_asset_id = database_mapping[table_name]
            else:
                # Try to find asset by name
                source_asset = self.db.query(models.Asset).filter(
                    models.Asset.asset_name.like(f"%{table_name}%")
                ).first()
                if source_asset:
                    source_asset_id = source_asset.asset_id

            if source_asset_id:
                edge_info = self.register_lineage(
                    source_asset_id=source_asset_id,
                    target_asset_id=target_asset_id,
                    transformation_type=transformation_type,
                    transformation_logic=sql_query,
                    column_mappings=column_mappings.get(table_name, {})
                )
                lineage_edges.append(edge_info)

        return {
            "edges_created": len(lineage_edges),
            "source_tables": source_tables,
            "transformation_type": transformation_type,
            "edges": lineage_edges
        }

    def get_lineage_path(
        self,
        asset_id: int,
        direction: str = "both",
        max_depth: int = 5
    ) -> Dict:
        """
        Get complete lineage path for an asset

        Args:
            asset_id: Asset ID to trace
            direction: "upstream", "downstream", or "both"
            max_depth: Maximum depth to traverse

        Returns:
            Dict with lineage path information
        """
        asset = self.db.query(models.Asset).filter(
            models.Asset.asset_id == asset_id
        ).first()

        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        upstream_path = []
        downstream_path = []

        if direction in ["upstream", "both"]:
            upstream_path = self._traverse_lineage(asset_id, "upstream", max_depth)

        if direction in ["downstream", "both"]:
            downstream_path = self._traverse_lineage(asset_id, "downstream", max_depth)

        return {
            "asset_id": asset_id,
            "asset_name": asset.asset_name,
            "upstream_lineage": {
                "depth": len(upstream_path),
                "path": upstream_path
            },
            "downstream_lineage": {
                "depth": len(downstream_path),
                "path": downstream_path
            }
        }

    def verify_lineage(self, edge_id: int) -> Dict:
        """
        Verify that a lineage edge is still valid

        Args:
            edge_id: Edge ID to verify

        Returns:
            Dict with verification status
        """
        edge = self.db.query(models_advanced.DataLineageEdge).filter(
            models_advanced.DataLineageEdge.edge_id == edge_id
        ).first()

        if not edge:
            raise ValueError(f"Edge {edge_id} not found")

        # Check if both nodes still exist
        source_node = self.db.query(models_advanced.DataLineageNode).filter(
            models_advanced.DataLineageNode.node_id == edge.source_node_id
        ).first()
        target_node = self.db.query(models_advanced.DataLineageNode).filter(
            models_advanced.DataLineageNode.node_id == edge.target_node_id
        ).first()

        is_valid = bool(source_node and target_node)

        if is_valid:
            edge.last_verified_at = datetime.utcnow()
        else:
            edge.is_active = False

        self.db.commit()

        return {
            "edge_id": edge_id,
            "is_valid": is_valid,
            "verified_at": edge.last_verified_at.isoformat() if is_valid else None
        }

    def _get_or_create_node(self, asset: models.Asset) -> models_advanced.DataLineageNode:
        """Get existing or create new lineage node for an asset"""
        node = self.db.query(models_advanced.DataLineageNode).filter(
            models_advanced.DataLineageNode.asset_id == asset.asset_id
        ).first()

        if not node:
            # Determine node type from asset type
            node_type_mapping = {
                "Database": models_advanced.LineageNodeType.TABLE,
                "API": models_advanced.LineageNodeType.API,
                "File": models_advanced.LineageNodeType.FILE,
                "Stream": models_advanced.LineageNodeType.STREAM,
            }

            node_type = node_type_mapping.get(
                asset.asset_type,
                models_advanced.LineageNodeType.TABLE
            )

            node = models_advanced.DataLineageNode(
                asset_id=asset.asset_id,
                node_type=node_type,
                node_name=asset.asset_name,
                location=asset.technical_details.get("location") if asset.technical_details else None,
                created_at=datetime.utcnow()
            )
            self.db.add(node)
            self.db.flush()

        return node

    def _extract_source_tables(self, sql_query: str) -> List[str]:
        """Extract table names from SQL query"""
        # Simple regex-based extraction (production would use proper SQL parser)
        sql_upper = sql_query.upper()
        tables = []

        # Extract from FROM clause
        from_pattern = r'FROM\s+([a-zA-Z0-9_\.]+)'
        from_matches = re.findall(from_pattern, sql_query, re.IGNORECASE)
        tables.extend(from_matches)

        # Extract from JOIN clauses
        join_pattern = r'JOIN\s+([a-zA-Z0-9_\.]+)'
        join_matches = re.findall(join_pattern, sql_query, re.IGNORECASE)
        tables.extend(join_matches)

        # Remove duplicates and clean
        tables = list(set([t.strip().split('.')[-1] for t in tables]))

        return tables

    def _detect_transformation_type(self, sql_query: str) -> str:
        """Detect type of transformation from SQL query"""
        sql_upper = sql_query.upper()

        if 'GROUP BY' in sql_upper or 'SUM(' in sql_upper or 'COUNT(' in sql_upper:
            return "AGGREGATE"
        elif 'JOIN' in sql_upper:
            return "JOIN"
        elif 'UNION' in sql_upper:
            return "UNION"
        elif 'WHERE' in sql_upper:
            return "FILTER"
        else:
            return "SELECT"

    def _extract_column_mappings(
        self,
        sql_query: str,
        source_tables: List[str]
    ) -> Dict[str, Dict]:
        """Extract column-level mappings from SQL query"""
        # Simplified column extraction
        # Production would use SQL AST parsing
        mappings = {}

        # Extract SELECT columns
        select_pattern = r'SELECT\s+(.*?)\s+FROM'
        select_match = re.search(select_pattern, sql_query, re.IGNORECASE | re.DOTALL)

        if select_match:
            columns_str = select_match.group(1)
            columns = [c.strip() for c in columns_str.split(',')]

            for table in source_tables:
                table_columns = [
                    col for col in columns
                    if table.lower() in col.lower() or '.' not in col
                ]
                if table_columns:
                    mappings[table] = {
                        "columns": table_columns,
                        "mapping_type": "direct"
                    }

        return mappings

    def _traverse_lineage(
        self,
        asset_id: int,
        direction: str,
        max_depth: int,
        current_depth: int = 0,
        visited: Optional[set] = None
    ) -> List[Dict]:
        """Recursively traverse lineage graph"""
        if visited is None:
            visited = set()

        if current_depth >= max_depth or asset_id in visited:
            return []

        visited.add(asset_id)

        # Get lineage node
        node = self.db.query(models_advanced.DataLineageNode).filter(
            models_advanced.DataLineageNode.asset_id == asset_id
        ).first()

        if not node:
            return []

        path = []

        if direction == "upstream":
            # Get incoming edges
            edges = self.db.query(models_advanced.DataLineageEdge).filter(
                and_(
                    models_advanced.DataLineageEdge.target_node_id == node.node_id,
                    models_advanced.DataLineageEdge.is_active == True
                )
            ).all()

            for edge in edges:
                source_node = self.db.query(models_advanced.DataLineageNode).filter(
                    models_advanced.DataLineageNode.node_id == edge.source_node_id
                ).first()

                if source_node and source_node.asset_id:
                    source_asset = self.db.query(models.Asset).filter(
                        models.Asset.asset_id == source_node.asset_id
                    ).first()

                    if source_asset:
                        step = {
                            "asset_id": source_asset.asset_id,
                            "asset_name": source_asset.asset_name,
                            "transformation": edge.transformation_type.value,
                            "depth": current_depth + 1
                        }
                        path.append(step)

                        # Recursive traversal
                        upstream = self._traverse_lineage(
                            source_asset.asset_id,
                            direction,
                            max_depth,
                            current_depth + 1,
                            visited
                        )
                        path.extend(upstream)

        else:  # downstream
            # Get outgoing edges
            edges = self.db.query(models_advanced.DataLineageEdge).filter(
                and_(
                    models_advanced.DataLineageEdge.source_node_id == node.node_id,
                    models_advanced.DataLineageEdge.is_active == True
                )
            ).all()

            for edge in edges:
                target_node = self.db.query(models_advanced.DataLineageNode).filter(
                    models_advanced.DataLineageNode.node_id == edge.target_node_id
                ).first()

                if target_node and target_node.asset_id:
                    target_asset = self.db.query(models.Asset).filter(
                        models.Asset.asset_id == target_node.asset_id
                    ).first()

                    if target_asset:
                        step = {
                            "asset_id": target_asset.asset_id,
                            "asset_name": target_asset.asset_name,
                            "transformation": edge.transformation_type.value,
                            "depth": current_depth + 1
                        }
                        path.append(step)

                        # Recursive traversal
                        downstream = self._traverse_lineage(
                            target_asset.asset_id,
                            direction,
                            max_depth,
                            current_depth + 1,
                            visited
                        )
                        path.extend(downstream)

        return path

    def bulk_import_lineage(
        self,
        lineage_data: List[Dict]
    ) -> Dict:
        """
        Bulk import lineage relationships from external system

        Args:
            lineage_data: List of lineage edge definitions

        Returns:
            Dict with import statistics
        """
        created_count = 0
        updated_count = 0
        failed_count = 0
        errors = []

        for edge_data in lineage_data:
            try:
                result = self.register_lineage(
                    source_asset_id=edge_data["source_asset_id"],
                    target_asset_id=edge_data["target_asset_id"],
                    transformation_type=edge_data["transformation_type"],
                    transformation_logic=edge_data.get("transformation_logic"),
                    column_mappings=edge_data.get("column_mappings"),
                    metadata=edge_data.get("metadata")
                )

                if "updated" in str(result):
                    updated_count += 1
                else:
                    created_count += 1

            except Exception as e:
                failed_count += 1
                errors.append({
                    "edge": edge_data,
                    "error": str(e)
                })

        return {
            "total_processed": len(lineage_data),
            "created": created_count,
            "updated": updated_count,
            "failed": failed_count,
            "errors": errors[:10]  # Return first 10 errors
        }
