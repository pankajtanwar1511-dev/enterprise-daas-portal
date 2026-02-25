"""
Schema Registry Service
Centralized schema management with versioning and compatibility checking
Supports Avro, JSON Schema, and Protobuf formats
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
from .. import models, models_advanced


class SchemaRegistry:
    """
    Manages schema versions with compatibility validation
    Ensures backward/forward compatibility across schema evolution
    """

    def __init__(self, db: Session):
        self.db = db

    def register_schema(
        self,
        subject: str,
        schema_format: str,
        schema_definition: Dict,
        compatibility_mode: str = "BACKWARD",
        asset_id: Optional[int] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Register a new schema or new version of existing schema

        Args:
            subject: Schema subject/name (e.g., "customer-events")
            schema_format: Format (AVRO, JSON_SCHEMA, PROTOBUF)
            schema_definition: The schema definition dict
            compatibility_mode: Compatibility mode (BACKWARD, FORWARD, FULL, NONE)
            asset_id: Associated asset ID
            description: Schema description

        Returns:
            Dict with registered schema information
        """
        # Get latest version for this subject
        latest_schema = self.db.query(models_advanced.SchemaRegistry).filter(
            models_advanced.SchemaRegistry.subject == subject
        ).order_by(desc(models_advanced.SchemaRegistry.version)).first()

        new_version = 1 if not latest_schema else latest_schema.version + 1

        # Check compatibility if not first version
        if latest_schema and compatibility_mode != "NONE":
            is_compatible, compatibility_errors = self._check_compatibility(
                old_schema=latest_schema.schema_definition,
                new_schema=schema_definition,
                compatibility_mode=compatibility_mode,
                schema_format=schema_format
            )

            if not is_compatible:
                raise ValueError(
                    f"Schema incompatible with version {latest_schema.version}: "
                    f"{', '.join(compatibility_errors)}"
                )

        # Create new schema version
        new_schema = models_advanced.SchemaRegistry(
            subject=subject,
            schema_format=models_advanced.SchemaFormat[schema_format],
            version=new_version,
            schema_definition=schema_definition,
            compatibility_mode=models_advanced.SchemaCompatibility[compatibility_mode],
            asset_id=asset_id,
            description=description,
            registered_at=datetime.utcnow(),
            is_latest=True
        )

        # Mark previous version as not latest
        if latest_schema:
            latest_schema.is_latest = False

        self.db.add(new_schema)
        self.db.commit()

        return {
            "schema_id": new_schema.schema_id,
            "subject": subject,
            "version": new_version,
            "schema_format": schema_format,
            "compatibility_mode": compatibility_mode,
            "registered_at": new_schema.registered_at.isoformat()
        }

    def get_schema(
        self,
        subject: str,
        version: Optional[int] = None
    ) -> Dict:
        """
        Get schema by subject and version

        Args:
            subject: Schema subject
            version: Specific version (if None, returns latest)

        Returns:
            Schema information with definition
        """
        query = self.db.query(models_advanced.SchemaRegistry).filter(
            models_advanced.SchemaRegistry.subject == subject
        )

        if version:
            schema = query.filter(
                models_advanced.SchemaRegistry.version == version
            ).first()
        else:
            schema = query.filter(
                models_advanced.SchemaRegistry.is_latest == True
            ).first()

        if not schema:
            raise ValueError(f"Schema not found: {subject} version {version or 'latest'}")

        return {
            "schema_id": schema.schema_id,
            "subject": schema.subject,
            "version": schema.version,
            "schema_format": schema.schema_format.value,
            "schema_definition": schema.schema_definition,
            "compatibility_mode": schema.compatibility_mode.value,
            "asset_id": schema.asset_id,
            "description": schema.description,
            "is_latest": schema.is_latest,
            "registered_at": schema.registered_at.isoformat()
        }

    def list_subjects(self) -> List[str]:
        """
        List all schema subjects

        Returns:
            List of unique schema subjects
        """
        subjects = self.db.query(
            models_advanced.SchemaRegistry.subject
        ).distinct().all()

        return [s[0] for s in subjects]

    def list_versions(self, subject: str) -> List[int]:
        """
        List all versions for a subject

        Args:
            subject: Schema subject

        Returns:
            List of version numbers
        """
        versions = self.db.query(
            models_advanced.SchemaRegistry.version
        ).filter(
            models_advanced.SchemaRegistry.subject == subject
        ).order_by(
            models_advanced.SchemaRegistry.version
        ).all()

        return [v[0] for v in versions]

    def check_compatibility(
        self,
        subject: str,
        new_schema: Dict,
        version: Optional[int] = None
    ) -> Dict:
        """
        Check if new schema is compatible with existing version

        Args:
            subject: Schema subject
            new_schema: New schema definition to check
            version: Version to check against (if None, checks latest)

        Returns:
            Dict with compatibility status and errors
        """
        # Get reference schema
        reference_schema = self.get_schema(subject, version)

        compatibility_mode = reference_schema["compatibility_mode"]
        schema_format = reference_schema["schema_format"]

        is_compatible, errors = self._check_compatibility(
            old_schema=reference_schema["schema_definition"],
            new_schema=new_schema,
            compatibility_mode=compatibility_mode,
            schema_format=schema_format
        )

        return {
            "is_compatible": is_compatible,
            "compatibility_mode": compatibility_mode,
            "reference_version": reference_schema["version"],
            "errors": errors
        }

    def compare_schemas(
        self,
        subject: str,
        version1: int,
        version2: int
    ) -> Dict:
        """
        Compare two schema versions and identify differences

        Args:
            subject: Schema subject
            version1: First version
            version2: Second version

        Returns:
            Dict with differences between schemas
        """
        schema1 = self.get_schema(subject, version1)
        schema2 = self.get_schema(subject, version2)

        diff = self._compute_schema_diff(
            schema1["schema_definition"],
            schema2["schema_definition"],
            schema1["schema_format"]
        )

        return {
            "subject": subject,
            "version1": version1,
            "version2": version2,
            "differences": diff
        }

    def validate_data_against_schema(
        self,
        subject: str,
        data: Dict,
        version: Optional[int] = None
    ) -> Dict:
        """
        Validate data against a schema

        Args:
            subject: Schema subject
            data: Data to validate
            version: Schema version (if None, uses latest)

        Returns:
            Dict with validation result
        """
        schema = self.get_schema(subject, version)

        # Create validation run record
        validation = models_advanced.SchemaValidation(
            schema_id=schema["schema_id"],
            validated_at=datetime.utcnow(),
            validation_result={},
            is_valid=False
        )

        try:
            is_valid, errors = self._validate_data(
                data=data,
                schema_definition=schema["schema_definition"],
                schema_format=schema["schema_format"]
            )

            validation.is_valid = is_valid
            validation.validation_result = {
                "data_sample": data,
                "errors": errors
            }

            self.db.add(validation)
            self.db.commit()

            return {
                "validation_id": validation.validation_id,
                "is_valid": is_valid,
                "schema_version": schema["version"],
                "errors": errors,
                "validated_at": validation.validated_at.isoformat()
            }

        except Exception as e:
            validation.is_valid = False
            validation.validation_result = {"error": str(e)}
            self.db.add(validation)
            self.db.commit()

            raise

    def _check_compatibility(
        self,
        old_schema: Dict,
        new_schema: Dict,
        compatibility_mode: str,
        schema_format: str
    ) -> Tuple[bool, List[str]]:
        """
        Check schema compatibility based on mode

        Returns:
            Tuple of (is_compatible, list_of_errors)
        """
        errors = []

        if compatibility_mode == "NONE":
            return True, []

        if schema_format == "JSON_SCHEMA":
            errors = self._check_json_schema_compatibility(
                old_schema, new_schema, compatibility_mode
            )
        elif schema_format == "AVRO":
            errors = self._check_avro_compatibility(
                old_schema, new_schema, compatibility_mode
            )
        else:
            # Generic compatibility check
            errors = self._check_generic_compatibility(
                old_schema, new_schema, compatibility_mode
            )

        return len(errors) == 0, errors

    def _check_json_schema_compatibility(
        self,
        old_schema: Dict,
        new_schema: Dict,
        mode: str
    ) -> List[str]:
        """Check JSON Schema compatibility"""
        errors = []

        old_props = old_schema.get("properties", {})
        new_props = new_schema.get("properties", {})
        old_required = set(old_schema.get("required", []))
        new_required = set(new_schema.get("required", []))

        if mode in ["BACKWARD", "FULL"]:
            # Backward: New schema can read old data
            # Cannot add required fields
            added_required = new_required - old_required
            if added_required:
                errors.append(f"Cannot add required fields: {added_required}")

            # Cannot remove fields that exist in old schema
            removed_fields = set(old_props.keys()) - set(new_props.keys())
            if removed_fields:
                errors.append(f"Cannot remove fields: {removed_fields}")

        if mode in ["FORWARD", "FULL"]:
            # Forward: Old schema can read new data
            # Cannot remove required fields
            removed_required = old_required - new_required
            if removed_required:
                errors.append(f"Cannot remove required fields: {removed_required}")

            # Cannot add fields without defaults
            added_fields = set(new_props.keys()) - set(old_props.keys())
            for field in added_fields:
                if field in new_required:
                    errors.append(f"Cannot add required field without default: {field}")

        return errors

    def _check_avro_compatibility(
        self,
        old_schema: Dict,
        new_schema: Dict,
        mode: str
    ) -> List[str]:
        """Check Avro schema compatibility"""
        errors = []

        old_fields = {f["name"]: f for f in old_schema.get("fields", [])}
        new_fields = {f["name"]: f for f in new_schema.get("fields", [])}

        if mode in ["BACKWARD", "FULL"]:
            # Cannot remove fields without defaults
            removed_fields = set(old_fields.keys()) - set(new_fields.keys())
            if removed_fields:
                errors.append(f"Cannot remove fields: {removed_fields}")

        if mode in ["FORWARD", "FULL"]:
            # Cannot add fields without defaults
            added_fields = set(new_fields.keys()) - set(old_fields.keys())
            for field_name in added_fields:
                field = new_fields[field_name]
                if "default" not in field:
                    errors.append(f"Field '{field_name}' added without default value")

        return errors

    def _check_generic_compatibility(
        self,
        old_schema: Dict,
        new_schema: Dict,
        mode: str
    ) -> List[str]:
        """Generic compatibility check for unknown schema formats"""
        errors = []

        # Simple field-level check
        old_keys = set(old_schema.keys())
        new_keys = set(new_schema.keys())

        if mode in ["BACKWARD", "FULL"]:
            removed_keys = old_keys - new_keys
            if removed_keys:
                errors.append(f"Fields removed: {removed_keys}")

        if mode in ["FORWARD", "FULL"]:
            added_keys = new_keys - old_keys
            if added_keys:
                errors.append(f"Fields added: {added_keys}")

        return errors

    def _compute_schema_diff(
        self,
        schema1: Dict,
        schema2: Dict,
        schema_format: str
    ) -> Dict:
        """Compute differences between two schemas"""
        diff = {
            "added_fields": [],
            "removed_fields": [],
            "modified_fields": [],
            "type_changes": []
        }

        # Get field sets
        if schema_format == "JSON_SCHEMA":
            fields1 = set(schema1.get("properties", {}).keys())
            fields2 = set(schema2.get("properties", {}).keys())
        elif schema_format == "AVRO":
            fields1 = {f["name"] for f in schema1.get("fields", [])}
            fields2 = {f["name"] for f in schema2.get("fields", [])}
        else:
            fields1 = set(schema1.keys())
            fields2 = set(schema2.keys())

        diff["added_fields"] = list(fields2 - fields1)
        diff["removed_fields"] = list(fields1 - fields2)

        # Check for type changes in common fields
        common_fields = fields1 & fields2
        for field in common_fields:
            if schema_format == "JSON_SCHEMA":
                type1 = schema1.get("properties", {}).get(field, {}).get("type")
                type2 = schema2.get("properties", {}).get(field, {}).get("type")
            else:
                type1 = str(schema1.get(field))
                type2 = str(schema2.get(field))

            if type1 != type2:
                diff["type_changes"].append({
                    "field": field,
                    "old_type": type1,
                    "new_type": type2
                })

        return diff

    def _validate_data(
        self,
        data: Dict,
        schema_definition: Dict,
        schema_format: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate data against schema

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        if schema_format == "JSON_SCHEMA":
            # Validate required fields
            required_fields = schema_definition.get("required", [])
            for field in required_fields:
                if field not in data:
                    errors.append(f"Missing required field: {field}")

            # Validate field types
            properties = schema_definition.get("properties", {})
            for field, value in data.items():
                if field in properties:
                    expected_type = properties[field].get("type")
                    actual_type = type(value).__name__

                    type_mapping = {
                        "str": "string",
                        "int": "integer",
                        "float": "number",
                        "bool": "boolean",
                        "list": "array",
                        "dict": "object"
                    }

                    if expected_type and type_mapping.get(actual_type) != expected_type:
                        errors.append(
                            f"Field '{field}' has wrong type: "
                            f"expected {expected_type}, got {actual_type}"
                        )

        return len(errors) == 0, errors
