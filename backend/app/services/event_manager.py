"""
Event Version Control and Catalog Management
Manages event schemas, producer/consumer dependencies, and version compatibility
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import Dict, List, Optional
from datetime import datetime
from .. import models, models_advanced


class EventManager:
    """
    Event catalog and version control management
    Tracks event producers, consumers, and schema evolution
    """

    def __init__(self, db: Session):
        self.db = db

    def register_event(
        self,
        event_name: str,
        schema_definition: Dict,
        schema_format: str = "JSON_SCHEMA",
        version: Optional[int] = None,
        producer_asset_id: Optional[int] = None,
        description: Optional[str] = None,
        compatibility_mode: str = "BACKWARD"
    ) -> Dict:
        """
        Register a new event or new version of existing event

        Args:
            event_name: Name of the event (e.g., "customer.created")
            schema_definition: Event schema definition
            schema_format: Schema format (JSON_SCHEMA, AVRO, PROTOBUF)
            version: Specific version (auto-increments if None)
            producer_asset_id: Asset that produces this event
            description: Event description
            compatibility_mode: Compatibility mode for schema evolution

        Returns:
            Dict with registered event information
        """
        # Check if event already exists
        existing = self.db.query(models_advanced.SchemaRegistry).filter(
            models_advanced.SchemaRegistry.subject == event_name
        ).order_by(models_advanced.SchemaRegistry.version.desc()).first()

        if existing:
            # Increment version
            new_version = existing.version + 1 if version is None else version

            # Mark previous version as not latest
            self.db.query(models_advanced.SchemaRegistry).filter(
                and_(
                    models_advanced.SchemaRegistry.subject == event_name,
                    models_advanced.SchemaRegistry.is_latest == True
                )
            ).update({"is_latest": False})
        else:
            new_version = version or 1

        # Create new event schema version
        event_schema = models_advanced.SchemaRegistry(
            subject=event_name,
            schema_format=models_advanced.SchemaFormat[schema_format],
            version=new_version,
            schema_definition=schema_definition,
            compatibility_mode=models_advanced.SchemaCompatibility[compatibility_mode],
            is_active=True,
            is_latest=True,
            asset_id=producer_asset_id,
            description=description,
            created_at=datetime.utcnow()
        )

        self.db.add(event_schema)
        self.db.commit()

        return {
            "schema_id": event_schema.schema_id,
            "event_name": event_name,
            "version": new_version,
            "schema_format": schema_format,
            "compatibility_mode": compatibility_mode,
            "producer_asset_id": producer_asset_id,
            "created_at": event_schema.created_at.isoformat()
        }

    def register_consumer(
        self,
        event_name: str,
        consumer_asset_id: int,
        version_constraint: Optional[str] = None
    ) -> Dict:
        """
        Register an asset as a consumer of an event

        Args:
            event_name: Event being consumed
            consumer_asset_id: Asset that consumes the event
            version_constraint: Version constraint (e.g., ">=1.0", "1.x", "*")

        Returns:
            Dict with registration information
        """
        # Get event schema
        event_schema = self.db.query(models_advanced.SchemaRegistry).filter(
            and_(
                models_advanced.SchemaRegistry.subject == event_name,
                models_advanced.SchemaRegistry.is_latest == True
            )
        ).first()

        if not event_schema:
            raise ValueError(f"Event {event_name} not found")

        # Verify consumer asset exists
        consumer = self.db.query(models.Asset).filter(
            models.Asset.asset_id == consumer_asset_id
        ).first()

        if not consumer:
            raise ValueError(f"Consumer asset {consumer_asset_id} not found")

        # Check if producer asset exists for this event
        if event_schema.asset_id:
            # Create lineage edge from producer to consumer
            existing_edge = self.db.query(models_advanced.DataLineageEdge).join(
                models_advanced.DataLineageNode,
                models_advanced.DataLineageEdge.source_node_id == models_advanced.DataLineageNode.node_id
            ).filter(
                and_(
                    models_advanced.DataLineageNode.asset_id == event_schema.asset_id,
                    models_advanced.DataLineageNode.node_name == event_name
                )
            ).first()

            if not existing_edge:
                # Create lineage nodes if they don't exist
                producer_node = self.db.query(models_advanced.DataLineageNode).filter(
                    and_(
                        models_advanced.DataLineageNode.asset_id == event_schema.asset_id,
                        models_advanced.DataLineageNode.node_name == event_name
                    )
                ).first()

                if not producer_node:
                    producer_node = models_advanced.DataLineageNode(
                        asset_id=event_schema.asset_id,
                        node_type=models_advanced.LineageNodeType.STREAM,
                        node_name=event_name,
                        description=f"Event stream: {event_name}",
                        schema_definition=event_schema.schema_definition,
                        created_at=datetime.utcnow()
                    )
                    self.db.add(producer_node)
                    self.db.flush()

                consumer_node = self.db.query(models_advanced.DataLineageNode).filter(
                    and_(
                        models_advanced.DataLineageNode.asset_id == consumer_asset_id,
                        models_advanced.DataLineageNode.node_name.like(f"%{consumer.asset_name}%")
                    )
                ).first()

                if not consumer_node:
                    consumer_node = models_advanced.DataLineageNode(
                        asset_id=consumer_asset_id,
                        node_type=models_advanced.LineageNodeType.STREAM,
                        node_name=f"{consumer.asset_name}_consumer",
                        description=f"Consumer of {event_name}",
                        created_at=datetime.utcnow()
                    )
                    self.db.add(consumer_node)
                    self.db.flush()

                # Create lineage edge
                lineage_edge = models_advanced.DataLineageEdge(
                    source_node_id=producer_node.node_id,
                    target_node_id=consumer_node.node_id,
                    transformation_type=models_advanced.TransformationType.EXTRACT,
                    transformation_logic=f"Consume event: {event_name} (version constraint: {version_constraint or '*'})",
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                self.db.add(lineage_edge)

        self.db.commit()

        return {
            "event_name": event_name,
            "consumer_asset_id": consumer_asset_id,
            "consumer_name": consumer.asset_name,
            "version_constraint": version_constraint or "*",
            "current_version": event_schema.version,
            "registered_at": datetime.utcnow().isoformat()
        }

    def get_event_catalog(
        self,
        search_query: Optional[str] = None,
        producer_asset_id: Optional[int] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """
        Get event catalog with search and filters

        Args:
            search_query: Search in event names and descriptions
            producer_asset_id: Filter by producer
            active_only: Only active events
            limit: Max events to return
            offset: Pagination offset

        Returns:
            Dict with event catalog
        """
        # Get latest version of each event
        query = self.db.query(models_advanced.SchemaRegistry).filter(
            models_advanced.SchemaRegistry.is_latest == True
        )

        if active_only:
            query = query.filter(models_advanced.SchemaRegistry.is_active == True)

        if producer_asset_id:
            query = query.filter(models_advanced.SchemaRegistry.asset_id == producer_asset_id)

        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.filter(
                or_(
                    models_advanced.SchemaRegistry.subject.like(search_pattern),
                    models_advanced.SchemaRegistry.description.like(search_pattern)
                )
            )

        total = query.count()
        events = query.limit(limit).offset(offset).all()

        event_list = []
        for event in events:
            # Get consumer count from lineage
            consumer_count = 0
            if event.asset_id:
                nodes = self.db.query(models_advanced.DataLineageNode).filter(
                    and_(
                        models_advanced.DataLineageNode.asset_id == event.asset_id,
                        models_advanced.DataLineageNode.node_name == event.subject
                    )
                ).all()

                for node in nodes:
                    consumer_count += len(node.downstream_edges)

            event_list.append({
                "event_name": event.subject,
                "version": event.version,
                "schema_format": event.schema_format.value,
                "compatibility_mode": event.compatibility_mode.value,
                "producer_asset_id": event.asset_id,
                "consumer_count": consumer_count,
                "is_active": event.is_active,
                "created_at": event.created_at.isoformat(),
                "description": event.description
            })

        return {
            "total": total,
            "count": len(event_list),
            "events": event_list
        }

    def get_event_versions(
        self,
        event_name: str
    ) -> List[Dict]:
        """
        Get all versions of an event

        Args:
            event_name: Event to get versions for

        Returns:
            List of event versions
        """
        versions = self.db.query(models_advanced.SchemaRegistry).filter(
            models_advanced.SchemaRegistry.subject == event_name
        ).order_by(models_advanced.SchemaRegistry.version.desc()).all()

        if not versions:
            raise ValueError(f"Event {event_name} not found")

        return [{
            "schema_id": v.schema_id,
            "version": v.version,
            "schema_definition": v.schema_definition,
            "is_active": v.is_active,
            "is_latest": v.is_latest,
            "created_at": v.created_at.isoformat(),
            "deprecated_at": v.deprecated_at.isoformat() if v.deprecated_at else None,
            "deprecated_reason": v.deprecated_reason
        } for v in versions]

    def get_consumers(
        self,
        event_name: str
    ) -> List[Dict]:
        """
        Get all consumers of an event

        Args:
            event_name: Event to get consumers for

        Returns:
            List of consumer assets
        """
        # Get event schema
        event_schema = self.db.query(models_advanced.SchemaRegistry).filter(
            and_(
                models_advanced.SchemaRegistry.subject == event_name,
                models_advanced.SchemaRegistry.is_latest == True
            )
        ).first()

        if not event_schema:
            raise ValueError(f"Event {event_name} not found")

        if not event_schema.asset_id:
            return []

        # Get lineage nodes for this event
        producer_nodes = self.db.query(models_advanced.DataLineageNode).filter(
            and_(
                models_advanced.DataLineageNode.asset_id == event_schema.asset_id,
                models_advanced.DataLineageNode.node_name == event_name
            )
        ).all()

        consumers = []
        for node in producer_nodes:
            for edge in node.downstream_edges:
                target_node = edge.target_node
                if target_node.asset_id:
                    asset = self.db.query(models.Asset).filter(
                        models.Asset.asset_id == target_node.asset_id
                    ).first()

                    if asset:
                        consumers.append({
                            "asset_id": asset.asset_id,
                            "asset_name": asset.asset_name,
                            "asset_type": asset.asset_type,
                            "environment": asset.environment,
                            "lineage_created_at": edge.created_at.isoformat()
                        })

        return consumers

    def check_breaking_changes(
        self,
        event_name: str,
        new_schema: Dict
    ) -> Dict:
        """
        Check if new schema introduces breaking changes

        Args:
            event_name: Event to check
            new_schema: Proposed new schema

        Returns:
            Dict with breaking change analysis
        """
        # Get current schema
        current = self.db.query(models_advanced.SchemaRegistry).filter(
            and_(
                models_advanced.SchemaRegistry.subject == event_name,
                models_advanced.SchemaRegistry.is_latest == True
            )
        ).first()

        if not current:
            return {
                "has_breaking_changes": False,
                "is_new_event": True,
                "message": "This is a new event"
            }

        # Simple breaking change detection for JSON schemas
        breaking_changes = []
        warnings = []

        if current.schema_format == models_advanced.SchemaFormat.JSON_SCHEMA:
            current_schema = current.schema_definition
            current_required = set(current_schema.get("required", []))
            new_required = set(new_schema.get("required", []))

            current_props = set(current_schema.get("properties", {}).keys())
            new_props = set(new_schema.get("properties", {}).keys())

            # Check for new required fields (breaking for backward compatibility)
            new_required_fields = new_required - current_required
            if new_required_fields:
                breaking_changes.append(f"New required fields added: {', '.join(new_required_fields)}")

            # Check for removed required fields (breaking for forward compatibility)
            removed_required_fields = current_required - new_required
            if removed_required_fields:
                breaking_changes.append(f"Required fields removed: {', '.join(removed_required_fields)}")

            # Check for removed properties
            removed_props = current_props - new_props
            if removed_props:
                warnings.append(f"Properties removed: {', '.join(removed_props)}")

            # Check for type changes
            for prop in current_props & new_props:
                current_type = current_schema["properties"][prop].get("type")
                new_type = new_schema["properties"][prop].get("type")
                if current_type != new_type:
                    breaking_changes.append(f"Type changed for {prop}: {current_type} -> {new_type}")

        has_breaking_changes = len(breaking_changes) > 0

        return {
            "has_breaking_changes": has_breaking_changes,
            "is_new_event": False,
            "current_version": current.version,
            "compatibility_mode": current.compatibility_mode.value,
            "breaking_changes": breaking_changes,
            "warnings": warnings,
            "recommendation": "Create new major version" if has_breaking_changes else "Safe to update"
        }

    def get_compatibility_matrix(
        self,
        event_name: str
    ) -> Dict:
        """
        Get version compatibility matrix for an event

        Args:
            event_name: Event to analyze

        Returns:
            Dict with compatibility matrix
        """
        versions = self.db.query(models_advanced.SchemaRegistry).filter(
            models_advanced.SchemaRegistry.subject == event_name
        ).order_by(models_advanced.SchemaRegistry.version).all()

        if not versions:
            raise ValueError(f"Event {event_name} not found")

        matrix = []
        for i, v1 in enumerate(versions):
            row = {
                "version": v1.version,
                "compatible_with": []
            }

            for v2 in versions:
                # Simple compatibility: same major version or consecutive versions
                v1_major = v1.version
                v2_major = v2.version

                is_compatible = (
                    v1_major == v2_major or
                    abs(v1_major - v2_major) <= 1
                )

                if is_compatible:
                    row["compatible_with"].append(v2.version)

            matrix.append(row)

        return {
            "event_name": event_name,
            "total_versions": len(versions),
            "compatibility_mode": versions[-1].compatibility_mode.value if versions else None,
            "matrix": matrix
        }

    def deprecate_event_version(
        self,
        event_name: str,
        version: int,
        reason: str
    ) -> Dict:
        """
        Deprecate a specific event version

        Args:
            event_name: Event name
            version: Version to deprecate
            reason: Deprecation reason

        Returns:
            Dict with deprecation info
        """
        event_schema = self.db.query(models_advanced.SchemaRegistry).filter(
            and_(
                models_advanced.SchemaRegistry.subject == event_name,
                models_advanced.SchemaRegistry.version == version
            )
        ).first()

        if not event_schema:
            raise ValueError(f"Event {event_name} version {version} not found")

        event_schema.is_active = False
        event_schema.deprecated_at = datetime.utcnow()
        event_schema.deprecated_reason = reason

        self.db.commit()

        return {
            "event_name": event_name,
            "version": version,
            "deprecated_at": event_schema.deprecated_at.isoformat(),
            "reason": reason
        }
