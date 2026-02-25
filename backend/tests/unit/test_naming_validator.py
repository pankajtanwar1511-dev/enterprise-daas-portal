"""
Unit tests for naming convention validator service
"""
import pytest
from app.services.naming_validator import NamingValidator


@pytest.mark.unit
class TestNamingValidatorFormat:
    """Test naming convention format validation"""

    def test_valid_naming_convention_basic(self, db, test_domain):
        """Test basic valid naming convention"""
        asset_name = "PROD-TEST-SYS-v1"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is True
        assert len(violations) == 0

    def test_invalid_naming_convention_system_too_long(self, db, test_domain):
        """Test invalid naming convention - system name too long (>10 chars)"""
        asset_name = "PROD-TEST-DATAWAREHOUSE-v1"  # DATAWAREHOUSE = 13 chars, max is 10
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False
        assert any("character" in v.lower() for v in violations)

    def test_valid_naming_convention_with_version_minor(self, db, test_domain):
        """Test valid naming convention with minor version"""
        asset_name = "PROD-TEST-SYS-v2.1"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is True
        assert len(violations) == 0

    def test_invalid_missing_environment(self, db, test_domain):
        """Test invalid naming convention - missing environment"""
        asset_name = "TEST-SYS-v1"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False
        assert len(violations) > 0
        assert any("format" in v.lower() for v in violations)

    def test_invalid_missing_version(self, db, test_domain):
        """Test invalid naming convention - missing version"""
        asset_name = "PROD-TEST-SYS"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False
        assert len(violations) > 0

    def test_invalid_lowercase(self, db, test_domain):
        """Test invalid naming convention - lowercase environment"""
        asset_name = "prod-test-sys-v1"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False
        assert any("environment" in v.lower() for v in violations)

    def test_invalid_wrong_separator(self, db, test_domain):
        """Test invalid naming convention - wrong separator"""
        asset_name = "PROD_TEST_SYS_v1"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False

    def test_invalid_empty_string(self, db):
        """Test invalid naming convention - empty string"""
        asset_name = ""
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False
        assert len(violations) > 0


@pytest.mark.unit
class TestEnvironmentValidation:
    """Test environment code validation"""

    def test_valid_environments(self, db, test_domain):
        """Test all valid environment codes"""
        valid_envs = ["DEV", "QA", "UAT", "PROD"]

        for env in valid_envs:
            asset_name = f"{env}-TEST-SYS-v1"
            is_valid, violations = NamingValidator.validate(asset_name, db)

            assert is_valid is True, f"Environment {env} should be valid"

    def test_invalid_environment(self, db, test_domain):
        """Test invalid environment code"""
        asset_name = "INVALID-TEST-SYS-v1"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False
        assert any("environment" in v.lower() for v in violations)

    def test_environment_case_sensitive(self, db, test_domain):
        """Test that environment codes are case-sensitive"""
        asset_name = "prod-TEST-SYS-v1"  # lowercase prod
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False


@pytest.mark.integration
class TestDomainValidation:
    """Test domain code validation"""

    def test_valid_domain_code(self, db, test_domain):
        """Test valid domain code from database"""
        asset_name = f"PROD-{test_domain.domain_code}-SYS-v1"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is True

    def test_invalid_domain_code(self, db):
        """Test invalid domain code not in database"""
        asset_name = "PROD-INVALID-SYS-v1"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False
        assert any("domain" in v.lower() for v in violations)

    def test_inactive_domain_code(self, db, test_domain):
        """Test inactive domain code"""
        # Deactivate domain
        test_domain.is_active = False
        db.commit()

        asset_name = f"PROD-{test_domain.domain_code}-SYS-v1"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False
        assert any("active" in v.lower() or "domain" in v.lower() for v in violations)


@pytest.mark.unit
class TestVersionValidation:
    """Test version format validation"""

    def test_valid_version_major_only(self, db, test_domain):
        """Test valid version with major only"""
        asset_name = "PROD-TEST-SYS-v1"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is True

    def test_valid_version_major_minor(self, db, test_domain):
        """Test valid version with major.minor"""
        asset_name = "PROD-TEST-SYS-v2.5"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is True

    def test_invalid_version_major_minor_patch(self, db, test_domain):
        """Test invalid version with major.minor.patch (not supported)"""
        asset_name = "PROD-TEST-SYS-v1.2.3"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False
        assert any("version" in v.lower() for v in violations)

    def test_invalid_version_missing_v_prefix(self, db, test_domain):
        """Test invalid version missing 'v' prefix"""
        asset_name = "PROD-TEST-SYS-1.0"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False
        assert any("version" in v.lower() for v in violations)

    def test_invalid_version_wrong_format(self, db, test_domain):
        """Test invalid version with wrong format"""
        asset_name = "PROD-TEST-SYS-version1"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False


@pytest.mark.unit
class TestSystemNameValidation:
    """Test system name component validation"""

    def test_valid_system_name_short(self, db, test_domain):
        """Test valid short system name"""
        asset_name = "PROD-TEST-SY-v1"  # 2 chars minimum
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is True

    def test_valid_system_name_long(self, db, test_domain):
        """Test valid long system name"""
        asset_name = "PROD-TEST-ABCDEFGHIJ-v1"  # 10 chars maximum
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is True

    def test_valid_system_name_alphanumeric(self, db, test_domain):
        """Test valid system name with numbers"""
        asset_name = "PROD-TEST-SYS123-v1"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is True

    def test_invalid_system_name_too_short(self, db, test_domain):
        """Test invalid system name too short"""
        asset_name = "PROD-TEST-S-v1"  # Only 1 char
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False

    def test_invalid_system_name_too_long(self, db, test_domain):
        """Test invalid system name too long"""
        asset_name = "PROD-TEST-ABCDEFGHIJK-v1"  # 11 chars
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False

    def test_invalid_system_name_special_chars(self, db, test_domain):
        """Test invalid system name with special characters"""
        asset_name = "PROD-TEST-SYS@#-v1"
        is_valid, violations = NamingValidator.validate(asset_name, db)

        assert is_valid is False
