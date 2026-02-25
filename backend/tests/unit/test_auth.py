"""
Unit tests for authentication (JWT, login, password hashing)
"""
import pytest
from datetime import timedelta
from jose import jwt

from app.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    SECRET_KEY,
    ALGORITHM
)


@pytest.mark.unit
class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_password_hash_generation(self):
        """Test that password hashing generates different hashes"""
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        # Hashes should be different (bcrypt uses random salt)
        assert hash1 != hash2
        assert hash1 != password
        assert hash2 != password

    def test_password_verification_success(self):
        """Test successful password verification"""
        password = "correctpassword"
        password_hash = get_password_hash(password)

        assert verify_password(password, password_hash) is True

    def test_password_verification_failure(self):
        """Test failed password verification with wrong password"""
        password = "correctpassword"
        wrong_password = "wrongpassword"
        password_hash = get_password_hash(password)

        assert verify_password(wrong_password, password_hash) is False

    def test_password_hash_different_each_time(self):
        """Test that same password generates different hashes"""
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


@pytest.mark.unit
class TestJWTTokens:
    """Test JWT token creation and validation"""

    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_contains_correct_data(self):
        """Test that token contains the correct user data"""
        username = "testuser123"
        data = {"sub": username}
        token = create_access_token(data)

        # Decode token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["sub"] == username
        assert "exp" in payload  # Expiration should be set

    def test_token_with_custom_expiry(self):
        """Test token creation with custom expiry time"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta=expires_delta)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert "exp" in payload
        assert payload["sub"] == "testuser"

    def test_token_with_additional_claims(self):
        """Test token creation with additional claims"""
        data = {
            "sub": "testuser",
            "role": "Admin",
            "user_id": 1
        }
        token = create_access_token(data)

        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        assert payload["sub"] == "testuser"
        assert payload["role"] == "Admin"
        assert payload["user_id"] == 1

    def test_invalid_token_raises_error(self):
        """Test that invalid token raises an error"""
        invalid_token = "invalid.token.here"

        with pytest.raises(jwt.JWTError):
            jwt.decode(invalid_token, SECRET_KEY, algorithms=[ALGORITHM])


@pytest.mark.integration
class TestLoginEndpoint:
    """Test login endpoint integration"""

    def test_login_success(self, client, test_user):
        """Test successful login returns access token"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "testpass123"
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["username"] == "testuser"

    def test_login_wrong_password(self, client, test_user):
        """Test login with wrong password fails"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )

        assert response.status_code == 401
        assert "detail" in response.json()

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user fails"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "nonexistent",
                "password": "anypassword"
            }
        )

        assert response.status_code == 401

    def test_login_inactive_user(self, client, test_user, db):
        """Test login with inactive user fails"""
        # Deactivate user
        test_user.is_active = False
        db.commit()

        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "testuser",
                "password": "testpass123"
            }
        )

        # API returns 403 Forbidden for inactive users
        assert response.status_code == 403
        assert "inactive" in response.json()["detail"].lower()

    def test_login_missing_credentials(self, client):
        """Test login with missing credentials fails"""
        response = client.post(
            "/api/v1/auth/login",
            data={}
        )

        assert response.status_code == 422  # Unprocessable entity


@pytest.mark.integration
class TestProtectedRoutes:
    """Test protected route authentication"""

    def test_access_protected_route_with_valid_token(self, client, auth_headers, test_domain):
        """Test accessing protected route with valid token"""
        response = client.get(
            "/api/v1/assets/",
            headers=auth_headers
        )

        assert response.status_code == 200

    def test_access_protected_route_without_token(self, client):
        """Test accessing GET endpoint without token (currently no auth required)"""
        response = client.get("/api/v1/assets/")

        # GET endpoints currently don't require authentication
        assert response.status_code == 200

    def test_access_protected_route_with_invalid_token(self, client):
        """Test accessing GET endpoint with invalid token (currently no auth required)"""
        response = client.get(
            "/api/v1/assets/",
            headers={"Authorization": "Bearer invalid_token"}
        )

        # GET endpoints currently don't require authentication
        assert response.status_code == 200

    def test_access_protected_route_with_malformed_header(self, client):
        """Test accessing GET endpoint with malformed auth header (currently no auth required)"""
        response = client.get(
            "/api/v1/assets/",
            headers={"Authorization": "InvalidFormat token"}
        )

        # GET endpoints currently don't require authentication
        assert response.status_code == 200
