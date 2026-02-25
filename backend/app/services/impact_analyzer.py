"""
Impact Analysis Engine
Analyzes what will be affected by changes to data assets

This is what separates a governance portal from a governance PLATFORM.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Dict, List, Set, Optional
from datetime import datetime
from .. import models, models_advanced
import networkx as nx


class ImpactAnalyzer:
    """
    Analyzes the impact of changes to data assets
    Uses graph traversal to find all dependencies
    """

    def __init__(self, db: Session):
        self.db = db
        self.dependency_graph = None

    def analyze_asset_change(
        self,
        asset_id: int,
        change_type: str,
        change_description: str = "",
        analysis_depth: int = 5
    ) -> Dict:
        """
        Perform comprehensive impact analysis for asset changes

        Args:
            asset_id: ID of the asset being changed
            change_type: Type of change (schema_change, deprecation, deletion, etc.)
            change_description: Detailed description of the change
            analysis_depth: How many hops to traverse (default 5)

        Returns:
            Dict with impact analysis results
        """
        asset = self.db.query(models.Asset).filter(models.Asset.asset_id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        # Build dependency graph
        self._build_dependency_graph()

        # Analyze upstream dependencies (what feeds this asset?)
        upstream_deps = self._find_upstream_dependencies(asset_id, max_depth=analysis_depth)

        # Analyze downstream dependencies (what consumes this asset?)
        downstream_deps = self._find_downstream_dependencies(asset_id, max_depth=analysis_depth)

        # Calculate impact score
        impact_score = self._calculate_impact_score(
            asset, change_type, upstream_deps, downstream_deps
        )

        # Find affected users and teams
        affected_info = self._find_affected_stakeholders(downstream_deps)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            asset, change_type, impact_score, downstream_deps
        )

        # Estimate migration effort
        migration_hours = self._estimate_migration_hours(
            change_type, len(downstream_deps), impact_score
        )

        # Save analysis result
        analysis = models_advanced.ImpactAnalysisRun(
            asset_id=asset_id,
            change_type=change_type,
            change_description=change_description,
            impact_score=impact_score,
            upstream_dependencies_count=len(upstream_deps),
            downstream_dependencies_count=len(downstream_deps),
            affected_assets=list(downstream_deps),
            affected_users_count=affected_info["user_count"],
            affected_teams=affected_info["teams"],
            migration_required=impact_score in ["HIGH", "CRITICAL"],
            estimated_migration_hours=migration_hours,
            recommended_actions=recommendations,
            analysis_depth=analysis_depth,
            analyzed_at=datetime.utcnow()
        )
        self.db.add(analysis)
        self.db.commit()

        return {
            "analysis_id": analysis.analysis_id,
            "asset_name": asset.asset_name,
            "change_type": change_type,
            "impact_score": impact_score,
            "upstream_dependencies": {
                "count": len(upstream_deps),
                "assets": [self._get_asset_info(aid) for aid in list(upstream_deps)[:10]]
            },
            "downstream_dependencies": {
                "count": len(downstream_deps),
                "assets": [self._get_asset_info(aid) for aid in list(downstream_deps)[:10]]
            },
            "affected_stakeholders": affected_info,
            "migration_required": impact_score in ["HIGH", "CRITICAL"],
            "estimated_migration_hours": migration_hours,
            "recommendations": recommendations,
            "analyzed_at": analysis.analyzed_at.isoformat()
        }

    def _build_dependency_graph(self):
        """Build directed graph of asset dependencies from lineage data"""
        self.dependency_graph = nx.DiGraph()

        # Add all assets as nodes
        assets = self.db.query(models.Asset).all()
        for asset in assets:
            self.dependency_graph.add_node(asset.asset_id, asset_name=asset.asset_name)

        # Add edges from lineage data
        edges = self.db.query(models_advanced.DataLineageEdge).filter(
            models_advanced.DataLineageEdge.is_active == True
        ).all()

        for edge in edges:
            # Get asset IDs from source and target nodes
            source_node = self.db.query(models_advanced.DataLineageNode).filter(
                models_advanced.DataLineageNode.node_id == edge.source_node_id
            ).first()
            target_node = self.db.query(models_advanced.DataLineageNode).filter(
                models_advanced.DataLineageNode.node_id == edge.target_node_id
            ).first()

            if source_node and target_node and source_node.asset_id and target_node.asset_id:
                self.dependency_graph.add_edge(
                    source_node.asset_id,
                    target_node.asset_id,
                    transformation=edge.transformation_type.value
                )

    def _find_upstream_dependencies(self, asset_id: int, max_depth: int = 5) -> Set[int]:
        """Find all assets that feed into this asset (sources)"""
        if not self.dependency_graph:
            return set()

        upstream = set()
        try:
            # Find all ancestors up to max_depth
            for depth in range(1, max_depth + 1):
                ancestors = nx.ancestors(self.dependency_graph, asset_id)
                upstream.update(ancestors)
        except nx.NetworkXError:
            pass

        return upstream

    def _find_downstream_dependencies(self, asset_id: int, max_depth: int = 5) -> Set[int]:
        """Find all assets that depend on this asset (consumers)"""
        if not self.dependency_graph:
            return set()

        downstream = set()
        try:
            # Find all descendants up to max_depth
            descendants = nx.descendants(self.dependency_graph, asset_id)
            downstream.update(descendants)
        except nx.NetworkXError:
            pass

        return downstream

    def _calculate_impact_score(
        self,
        asset: models.Asset,
        change_type: str,
        upstream_deps: Set[int],
        downstream_deps: Set[int]
    ) -> str:
        """
        Calculate impact score: LOW, MEDIUM, HIGH, CRITICAL

        Factors:
        - Number of downstream dependencies
        - Asset environment (PROD > QA > DEV)
        - Change type severity
        - Asset lifecycle stage
        """
        score = 0

        # Downstream dependency count
        downstream_count = len(downstream_deps)
        if downstream_count == 0:
            score += 0
        elif downstream_count <= 3:
            score += 1
        elif downstream_count <= 10:
            score += 2
        else:
            score += 3

        # Environment criticality
        if asset.environment == "PROD":
            score += 3
        elif asset.environment == "UAT":
            score += 2
        elif asset.environment == "QA":
            score += 1

        # Change type severity
        severity_map = {
            "schema_change": 3,
            "deletion": 4,
            "deprecation": 2,
            "policy_change": 1,
            "metadata_update": 0
        }
        score += severity_map.get(change_type, 1)

        # Lifecycle stage
        if asset.lifecycle_stage == "Active":
            score += 2
        elif asset.lifecycle_stage == "Deprecated":
            score += 1

        # Map score to category
        if score >= 9:
            return "CRITICAL"
        elif score >= 6:
            return "HIGH"
        elif score >= 3:
            return "MEDIUM"
        else:
            return "LOW"

    def _find_affected_stakeholders(self, affected_asset_ids: Set[int]) -> Dict:
        """Find users and teams affected by the change"""
        affected_users = set()
        affected_teams = set()

        for asset_id in affected_asset_ids:
            asset = self.db.query(models.Asset).filter(models.Asset.asset_id == asset_id).first()
            if asset:
                affected_users.add(asset.owner_id)
                if asset.domain:
                    affected_teams.add(asset.domain.domain_name)

        return {
            "user_count": len(affected_users),
            "teams": list(affected_teams),
            "users": list(affected_users)
        }

    def _generate_recommendations(
        self,
        asset: models.Asset,
        change_type: str,
        impact_score: str,
        downstream_deps: Set[int]
    ) -> List[str]:
        """Generate actionable recommendations based on impact analysis"""
        recommendations = []

        if impact_score in ["HIGH", "CRITICAL"]:
            recommendations.append("Schedule change review with Data Governance team")
            recommendations.append("Create detailed migration plan with timeline")
            recommendations.append("Notify all affected asset owners at least 2 weeks in advance")

        if change_type == "schema_change":
            recommendations.append("Provide backward-compatible schema version if possible")
            recommendations.append("Run schema compatibility validation")
            recommendations.append("Update documentation with schema changes")

        if change_type == "deprecation":
            recommendations.append("Set deprecation timeline (minimum 90 days)")
            recommendations.append("Provide migration guide to replacement asset")
            recommendations.append("Monitor usage metrics to ensure migration completion")

        if change_type == "deletion":
            recommendations.append("Ensure all downstream dependencies have migrated")
            recommendations.append("Archive data before deletion (retention policy)")
            recommendations.append("Obtain approval from all affected asset owners")

        if len(downstream_deps) > 0:
            recommendations.append(f"Contact owners of {len(downstream_deps)} dependent assets")
            recommendations.append("Coordinate deployment windows to minimize disruption")

        if asset.environment == "PROD":
            recommendations.append("Implement change in lower environments first (DEV → QA → UAT)")
            recommendations.append("Create rollback plan with tested procedures")

        return recommendations

    def _estimate_migration_hours(
        self,
        change_type: str,
        affected_count: int,
        impact_score: str
    ) -> float:
        """Estimate migration effort in hours"""
        base_hours = {
            "schema_change": 8,
            "deprecation": 16,
            "deletion": 24,
            "policy_change": 4,
            "metadata_update": 1
        }

        base = base_hours.get(change_type, 8)

        # Multiply by affected asset count (with diminishing returns)
        import math
        if affected_count > 0:
            multiplier = 1 + math.log(affected_count + 1)
        else:
            multiplier = 1

        # Add complexity factor based on impact score
        complexity = {
            "LOW": 1.0,
            "MEDIUM": 1.5,
            "HIGH": 2.0,
            "CRITICAL": 3.0
        }

        total_hours = base * multiplier * complexity.get(impact_score, 1.0)

        return round(total_hours, 1)

    def _get_asset_info(self, asset_id: int) -> Dict:
        """Get basic asset information"""
        asset = self.db.query(models.Asset).filter(models.Asset.asset_id == asset_id).first()
        if not asset:
            return {}

        return {
            "asset_id": asset.asset_id,
            "asset_name": asset.asset_name,
            "environment": asset.environment,
            "lifecycle_stage": asset.lifecycle_stage,
            "owner_id": asset.owner_id
        }

    def get_dependency_graph_visualization(self, asset_id: int) -> Dict:
        """
        Generate data for dependency graph visualization
        Returns nodes and edges suitable for D3.js or React Flow
        """
        self._build_dependency_graph()

        # Get subgraph around this asset (2 hops up and down)
        upstream = self._find_upstream_dependencies(asset_id, max_depth=2)
        downstream = self._find_downstream_dependencies(asset_id, max_depth=2)

        all_nodes = upstream | downstream | {asset_id}

        nodes = []
        edges = []

        for node_id in all_nodes:
            asset = self.db.query(models.Asset).filter(models.Asset.asset_id == node_id).first()
            if asset:
                nodes.append({
                    "id": node_id,
                    "label": asset.asset_name,
                    "type": "asset",
                    "environment": asset.environment,
                    "is_central": node_id == asset_id
                })

        # Get edges within subgraph
        for source, target in self.dependency_graph.edges():
            if source in all_nodes and target in all_nodes:
                edges.append({
                    "source": source,
                    "target": target,
                    "transformation": self.dependency_graph[source][target].get("transformation", "")
                })

        return {
            "nodes": nodes,
            "edges": edges,
            "central_asset_id": asset_id
        }
