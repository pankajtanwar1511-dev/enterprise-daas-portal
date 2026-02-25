"""
CI/CD Policy Enforcement Engine
Validates governance policies in deployment pipelines
Supports GitHub Actions, GitLab CI, and Jenkins integrations
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re
from .. import models, models_advanced


class PolicyEnforcer:
    """
    Enforces governance policies in CI/CD pipelines
    Validates naming conventions, documentation, data classification, etc.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_policy(
        self,
        policy_name: str,
        policy_type: str,
        policy_definition: Dict,
        is_blocking: bool = True,
        enforcement_level: str = "strict",
        applies_to_domains: Optional[List[str]] = None,
        applies_to_environments: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> Dict:
        """
        Create a new governance policy

        Args:
            policy_name: Unique policy name
            policy_type: NAMING_CONVENTION, DOCUMENTATION, DATA_CLASSIFICATION, OWNER_ASSIGNMENT
            policy_definition: Policy rules and configuration
            is_blocking: Whether to block deployment on violation
            enforcement_level: "strict", "warn", "audit"
            applies_to_domains: List of domain names (None = all domains)
            applies_to_environments: List of environments (None = all envs)
            description: Policy description

        Returns:
            Dict with created policy information
        """
        policy = models_advanced.GovernancePolicy(
            policy_name=policy_name,
            policy_type=models_advanced.PolicyType[policy_type],
            policy_definition=policy_definition,
            is_blocking=is_blocking,
            enforcement_level=enforcement_level,
            applies_to_domains=applies_to_domains or [],
            applies_to_environments=applies_to_environments or [],
            is_active=True,
            description=description,
            created_at=datetime.utcnow()
        )

        self.db.add(policy)
        self.db.commit()

        return {
            "policy_id": policy.policy_id,
            "policy_name": policy_name,
            "policy_type": policy_type,
            "is_blocking": is_blocking,
            "enforcement_level": enforcement_level,
            "created_at": policy.created_at.isoformat()
        }

    def validate_asset(
        self,
        asset_data: Dict,
        pipeline_context: Optional[Dict] = None
    ) -> Dict:
        """
        Validate asset data against all applicable policies

        Args:
            asset_data: Asset metadata to validate
            pipeline_context: CI/CD context (branch, commit, author, etc.)

        Returns:
            Dict with validation result and policy violations
        """
        # Get applicable policies
        policies = self._get_applicable_policies(asset_data)

        violations = []
        warnings = []
        passed_policies = []

        for policy in policies:
            result = self._validate_against_policy(asset_data, policy)

            if not result["passed"]:
                if policy.is_blocking:
                    violations.append({
                        "policy_id": policy.policy_id,
                        "policy_name": policy.policy_name,
                        "policy_type": policy.policy_type.value,
                        "severity": "ERROR",
                        "message": result["message"],
                        "details": result["details"]
                    })
                else:
                    warnings.append({
                        "policy_id": policy.policy_id,
                        "policy_name": policy.policy_name,
                        "policy_type": policy.policy_type.value,
                        "severity": "WARNING",
                        "message": result["message"],
                        "details": result["details"]
                    })
            else:
                passed_policies.append(policy.policy_name)

        # Record validation
        validation = models_advanced.PolicyValidation(
            validated_at=datetime.utcnow(),
            asset_name=asset_data.get("asset_name", "Unknown"),
            policy_violations=violations + warnings,
            passed=len(violations) == 0,
            pipeline_context=pipeline_context or {}
        )

        self.db.add(validation)
        self.db.commit()

        return {
            "validation_id": validation.validation_id,
            "passed": validation.passed,
            "can_deploy": len(violations) == 0,
            "total_policies_checked": len(policies),
            "passed_policies": len(passed_policies),
            "violations": violations,
            "warnings": warnings,
            "validated_at": validation.validated_at.isoformat()
        }

    def validate_naming_convention(
        self,
        asset_name: str,
        expected_pattern: Optional[str] = None
    ) -> Dict:
        """
        Validate asset naming against standard convention

        Default pattern: {ENV}-{DOMAIN}-{SYSTEM}-{VERSION}
        Example: PROD-SALES-CUSTOMER-v1

        Args:
            asset_name: Asset name to validate
            expected_pattern: Custom regex pattern (optional)

        Returns:
            Dict with validation result
        """
        # Default pattern: ENV-DOMAIN-SYSTEM-VERSION
        pattern = expected_pattern or r"^(DEV|QA|UAT|PROD)-([A-Z]+)-([A-Z0-9_]+)-(v\d+)$"

        match = re.match(pattern, asset_name)

        if match:
            components = match.groups() if expected_pattern is None else []
            return {
                "valid": True,
                "asset_name": asset_name,
                "pattern": pattern,
                "components": {
                    "environment": components[0] if len(components) > 0 else None,
                    "domain": components[1] if len(components) > 1 else None,
                    "system": components[2] if len(components) > 2 else None,
                    "version": components[3] if len(components) > 3 else None
                } if components else {}
            }
        else:
            return {
                "valid": False,
                "asset_name": asset_name,
                "pattern": pattern,
                "error": f"Name does not match expected pattern: {pattern}",
                "suggestion": "Use format: {ENV}-{DOMAIN}-{SYSTEM}-{VERSION} (e.g., PROD-SALES-CUSTOMER-v1)"
            }

    def validate_documentation(
        self,
        asset_data: Dict,
        required_fields: Optional[List[str]] = None
    ) -> Dict:
        """
        Validate that asset has required documentation fields

        Args:
            asset_data: Asset metadata
            required_fields: List of required field names

        Returns:
            Dict with validation result
        """
        default_required = [
            "description",
            "owner_id",
            "business_purpose",
            "data_classification"
        ]

        required = required_fields or default_required
        missing_fields = []

        for field in required:
            value = asset_data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field)

        return {
            "valid": len(missing_fields) == 0,
            "required_fields": required,
            "missing_fields": missing_fields,
            "completeness_percent": round((len(required) - len(missing_fields)) / len(required) * 100, 2)
        }

    def validate_data_classification(
        self,
        asset_data: Dict
    ) -> Dict:
        """
        Validate that asset has proper data classification

        Args:
            asset_data: Asset metadata

        Returns:
            Dict with validation result
        """
        valid_classifications = ["Public", "Internal", "Confidential", "Restricted"]
        classification = asset_data.get("data_classification")

        if not classification:
            return {
                "valid": False,
                "error": "Data classification is required",
                "valid_values": valid_classifications
            }

        if classification not in valid_classifications:
            return {
                "valid": False,
                "error": f"Invalid data classification: {classification}",
                "provided": classification,
                "valid_values": valid_classifications
            }

        # Additional checks based on classification level
        if classification in ["Confidential", "Restricted"]:
            # These require additional fields
            missing_security_fields = []

            if not asset_data.get("encryption_required"):
                missing_security_fields.append("encryption_required")
            if not asset_data.get("access_control_policy"):
                missing_security_fields.append("access_control_policy")

            if missing_security_fields:
                return {
                    "valid": False,
                    "classification": classification,
                    "error": f"{classification} data requires additional security fields",
                    "missing_fields": missing_security_fields
                }

        return {
            "valid": True,
            "classification": classification
        }

    def generate_github_action_config(
        self,
        asset_name_var: str = "${{ env.ASSET_NAME }}"
    ) -> str:
        """
        Generate GitHub Actions workflow configuration for policy validation

        Args:
            asset_name_var: GitHub Actions variable for asset name

        Returns:
            YAML configuration string
        """
        config = f"""
name: Data Governance Policy Check

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  governance-check:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Validate Data Governance Policies
        run: |
          curl -X POST ${{{{ secrets.GOVERNANCE_PORTAL_URL }}}}/api/v1/policies/validate \\
            -H "Content-Type: application/json" \\
            -H "Authorization: Bearer ${{{{ secrets.GOVERNANCE_API_TOKEN }}}}" \\
            -d '{{
              "asset_name": "{asset_name_var}",
              "description": "${{{{ github.event.head_commit.message }}}}",
              "owner_id": "${{{{ github.actor }}}}",
              "environment": "PROD",
              "pipeline_context": {{
                "branch": "${{{{ github.ref }}}}",
                "commit": "${{{{ github.sha }}}}",
                "author": "${{{{ github.actor }}}}"
              }}
            }}' \\
            -o validation_result.json

      - name: Check Validation Result
        run: |
          PASSED=$(jq -r '.passed' validation_result.json)
          if [ "$PASSED" != "true" ]; then
            echo "❌ Governance policy validation failed!"
            jq '.violations' validation_result.json
            exit 1
          else
            echo "✅ All governance policies passed"
          fi

      - name: Upload Validation Report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: governance-validation-report
          path: validation_result.json
"""
        return config

    def generate_gitlab_ci_config(self) -> str:
        """Generate GitLab CI configuration for policy validation"""
        config = """
governance_check:
  stage: validate
  image: curlimages/curl:latest
  script:
    - |
      curl -X POST ${GOVERNANCE_PORTAL_URL}/api/v1/policies/validate \\
        -H "Content-Type: application/json" \\
        -H "Authorization: Bearer ${GOVERNANCE_API_TOKEN}" \\
        -d "{
          \\"asset_name\\": \\"${ASSET_NAME}\\",
          \\"description\\": \\"${CI_COMMIT_MESSAGE}\\",
          \\"owner_id\\": \\"${GITLAB_USER_LOGIN}\\",
          \\"environment\\": \\"PROD\\",
          \\"pipeline_context\\": {
            \\"branch\\": \\"${CI_COMMIT_REF_NAME}\\",
            \\"commit\\": \\"${CI_COMMIT_SHA}\\",
            \\"author\\": \\"${GITLAB_USER_LOGIN}\\"
          }
        }" \\
        -o validation_result.json
    - |
      PASSED=$(cat validation_result.json | jq -r '.passed')
      if [ "$PASSED" != "true" ]; then
        echo "❌ Governance policy validation failed!"
        cat validation_result.json | jq '.violations'
        exit 1
      else
        echo "✅ All governance policies passed"
      fi
  artifacts:
    reports:
      junit: validation_result.json
    when: always
"""
        return config

    def _get_applicable_policies(self, asset_data: Dict) -> List[models_advanced.GovernancePolicy]:
        """Get policies that apply to this asset"""
        query = self.db.query(models_advanced.GovernancePolicy).filter(
            models_advanced.GovernancePolicy.is_active == True
        )

        policies = query.all()

        # Filter by domain and environment
        domain = asset_data.get("domain")
        environment = asset_data.get("environment")

        applicable = []
        for policy in policies:
            # Check domain applicability
            if policy.applies_to_domains:
                if not domain or domain not in policy.applies_to_domains:
                    continue

            # Check environment applicability
            if policy.applies_to_environments:
                if not environment or environment not in policy.applies_to_environments:
                    continue

            applicable.append(policy)

        return applicable

    def _validate_against_policy(
        self,
        asset_data: Dict,
        policy: models_advanced.GovernancePolicy
    ) -> Dict:
        """Validate asset data against a specific policy"""
        policy_type = policy.policy_type

        if policy_type == models_advanced.PolicyType.NAMING_CONVENTION:
            result = self.validate_naming_convention(
                asset_data.get("asset_name", ""),
                policy.policy_definition.get("pattern")
            )
            return {
                "passed": result["valid"],
                "message": result.get("error", "Naming convention validated"),
                "details": result
            }

        elif policy_type == models_advanced.PolicyType.DOCUMENTATION:
            result = self.validate_documentation(
                asset_data,
                policy.policy_definition.get("required_fields")
            )
            return {
                "passed": result["valid"],
                "message": f"Missing required fields: {', '.join(result['missing_fields'])}" if result['missing_fields'] else "Documentation complete",
                "details": result
            }

        elif policy_type == models_advanced.PolicyType.DATA_CLASSIFICATION:
            result = self.validate_data_classification(asset_data)
            return {
                "passed": result["valid"],
                "message": result.get("error", "Data classification validated"),
                "details": result
            }

        elif policy_type == models_advanced.PolicyType.OWNER_ASSIGNMENT:
            owner_id = asset_data.get("owner_id")
            return {
                "passed": bool(owner_id),
                "message": "Owner must be assigned" if not owner_id else "Owner assigned",
                "details": {"owner_id": owner_id}
            }

        else:
            return {
                "passed": True,
                "message": f"Unknown policy type: {policy_type.value}",
                "details": {}
            }

    def get_policy_statistics(self) -> Dict:
        """Get policy enforcement statistics"""
        total_policies = self.db.query(models_advanced.GovernancePolicy).count()
        enabled_policies = self.db.query(models_advanced.GovernancePolicy).filter(
            models_advanced.GovernancePolicy.is_active == True
        ).count()

        total_validations = self.db.query(models_advanced.PolicyValidation).count()
        passed_validations = self.db.query(models_advanced.PolicyValidation).filter(
            models_advanced.PolicyValidation.passed == True
        ).count()

        # Count by policy type
        type_counts = self.db.query(
            models_advanced.GovernancePolicy.policy_type,
            func.count(models_advanced.GovernancePolicy.policy_id)
        ).group_by(
            models_advanced.GovernancePolicy.policy_type
        ).all()

        return {
            "total_policies": total_policies,
            "enabled_policies": enabled_policies,
            "disabled_policies": total_policies - enabled_policies,
            "total_validations": total_validations,
            "passed_validations": passed_validations,
            "failed_validations": total_validations - passed_validations,
            "pass_rate": round(passed_validations / total_validations * 100, 2) if total_validations > 0 else None,
            "policies_by_type": {
                ptype.value: count for ptype, count in type_counts
            }
        }
