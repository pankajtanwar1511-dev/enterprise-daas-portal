"""
Naming Convention Validator Service
Validates asset names against the enterprise standard: ENV-DOMAIN-SYSTEM-VERSION
"""
import re
from typing import Tuple, List
from sqlalchemy.orm import Session
from ..models import Domain, Asset


class NamingValidator:
    """
    Validates asset names against naming convention standard.
    Format: {ENV}-{DOMAIN}-{SYSTEM}-{VERSION}
    Example: PROD-HR-DW-v1
    """

    VALID_ENVIRONMENTS = ["DEV", "QA", "UAT", "PROD"]
    SYSTEM_MIN_LENGTH = 2
    SYSTEM_MAX_LENGTH = 10

    @staticmethod
    def validate(asset_name: str, db: Session, exclude_asset_id: int = None) -> Tuple[bool, List[str]]:
        """
        Validate asset name against naming convention.

        Args:
            asset_name: The asset name to validate
            db: Database session
            exclude_asset_id: Optional asset ID to exclude from duplicate check (for updates)

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_violations)
        """
        violations = []

        # Check format structure
        parts = asset_name.split('-')
        if len(parts) != 4:
            violations.append("Format must be ENV-DOMAIN-SYSTEM-VERSION (exactly 4 components separated by hyphens)")
            return False, violations

        env, domain, system, version = parts

        # Validate environment
        if env not in NamingValidator.VALID_ENVIRONMENTS:
            violations.append(
                f"Invalid environment: '{env}'. Must be one of: {', '.join(NamingValidator.VALID_ENVIRONMENTS)}"
            )

        # Validate domain
        domain_obj = db.query(Domain).filter(
            Domain.domain_code == domain,
            Domain.is_active == True
        ).first()

        if not domain_obj:
            violations.append(
                f"Domain '{domain}' not approved. See approved domains list."
            )

        # Validate system name
        if not system.isalnum():
            violations.append(
                f"System name '{system}' contains invalid characters. Use A-Z, 0-9 only (no special characters)."
            )

        if len(system) < NamingValidator.SYSTEM_MIN_LENGTH or len(system) > NamingValidator.SYSTEM_MAX_LENGTH:
            violations.append(
                f"System name must be {NamingValidator.SYSTEM_MIN_LENGTH}-{NamingValidator.SYSTEM_MAX_LENGTH} characters. Current: {len(system)}"
            )

        # Validate version
        version_pattern = r'^v\d+(\.\d+)?$'
        if not re.match(version_pattern, version):
            violations.append(
                f"Version must be in format v{{major}} or v{{major}}.{{minor}} (e.g., v1 or v2.1). Current: '{version}'"
            )

        # Check for duplicates (exclude current asset if updating)
        query = db.query(Asset).filter(Asset.asset_name == asset_name)
        if exclude_asset_id:
            query = query.filter(Asset.asset_id != exclude_asset_id)
        existing = query.first()

        if existing:
            violations.append(
                f"Asset name '{asset_name}' already exists (Asset ID: {existing.asset_id})"
            )

        return len(violations) == 0, violations

    @staticmethod
    def suggest_corrections(asset_name: str, db: Session) -> List[str]:
        """
        Provide suggestions for non-compliant names.
        """
        suggestions = []

        parts = asset_name.split('-')
        if len(parts) != 4:
            suggestions.append("Use format: ENV-DOMAIN-SYSTEM-VERSION")
            suggestions.append("Example: PROD-HR-DW-v1")
            return suggestions

        env, domain, system, version = parts

        # Environment suggestions
        if env not in NamingValidator.VALID_ENVIRONMENTS:
            if env.upper() in NamingValidator.VALID_ENVIRONMENTS:
                suggestions.append(f"Convert environment to uppercase: {env.upper()}")
            elif env.lower() in ['production', 'prod']:
                suggestions.append("Use 'PROD' instead of 'production'")
            elif env.lower() in ['development', 'dev']:
                suggestions.append("Use 'DEV' instead of 'development'")
            elif env.lower() in ['test', 'testing']:
                suggestions.append("Use 'QA' for testing environments")

        # System suggestions
        if '_' in system:
            suggestions.append(f"Remove underscores from system name: {system.replace('_', '')}")
        if ' ' in system:
            suggestions.append(f"Remove spaces from system name: {system.replace(' ', '')}")

        # Version suggestions
        if not version.startswith('v'):
            if version.replace('.', '').isdigit():
                suggestions.append(f"Add 'v' prefix to version: v{version}")

        return suggestions
