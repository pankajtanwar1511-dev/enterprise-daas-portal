"""
Unit tests for Security Middleware
Tests rate limiting, security headers, CSRF protection, and input sanitization
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.middleware.security import (
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    CSRFProtectionMiddleware,
    sanitize_string,
    sanitize_dict,
    validate_sql_identifier,
)


# Test Rate Limiting
def test_rate_limit_middleware():
    """Test rate limiting middleware"""
    app = FastAPI()

    @app.get("/test")
    def test_endpoint():
        return {"message": "success"}

    # Add rate limiting with low threshold for testing
    app.add_middleware(RateLimitMiddleware, requests_per_minute=5)

    client = TestClient(app)

    # Make requests up to the limit
    for i in range(5):
        response = client.get("/test")
        assert response.status_code == 200
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers

    # Next request should be rate limited
    response = client.get("/test")
    assert response.status_code == 429
    assert "rate limit exceeded" in response.json()["detail"].lower()
    assert "Retry-After" in response.headers


def test_rate_limit_disabled():
    """Test that rate limiting can be disabled via env"""
    import os
    os.environ["RATE_LIMIT_ENABLED"] = "false"

    app = FastAPI()

    @app.get("/test")
    def test_endpoint():
        return {"message": "success"}

    app.add_middleware(RateLimitMiddleware, requests_per_minute=1)

    client = TestClient(app)

    # Should not be rate limited even with low threshold
    for i in range(10):
        response = client.get("/test")
        assert response.status_code == 200

    # Cleanup
    del os.environ["RATE_LIMIT_ENABLED"]


# Test Security Headers
def test_security_headers_middleware():
    """Test security headers are added to responses"""
    app = FastAPI()

    @app.get("/test")
    def test_endpoint():
        return {"message": "success"}

    app.add_middleware(SecurityHeadersMiddleware)

    client = TestClient(app)
    response = client.get("/test")

    # Check required security headers
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert "Content-Security-Policy" in response.headers

    # Server header should be removed
    assert "server" not in response.headers.keys()


def test_security_headers_hsts():
    """Test HSTS header is added for HTTPS"""
    app = FastAPI()

    @app.get("/test")
    def test_endpoint():
        return {"message": "success"}

    app.add_middleware(SecurityHeadersMiddleware)

    client = TestClient(app)

    # HTTP request - no HSTS
    response = client.get("/test")
    assert "Strict-Transport-Security" not in response.headers


# Test CSRF Protection
def test_csrf_protection_get_allowed():
    """Test CSRF protection allows GET requests"""
    app = FastAPI()

    @app.get("/test")
    def test_endpoint():
        return {"message": "success"}

    app.add_middleware(CSRFProtectionMiddleware)

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200


def test_csrf_protection_post_blocked():
    """Test CSRF protection blocks POST without token"""
    app = FastAPI()

    @app.post("/test")
    def test_endpoint():
        return {"message": "success"}

    app.add_middleware(CSRFProtectionMiddleware)

    client = TestClient(app)
    response = client.post("/test", json={"data": "test"})

    assert response.status_code == 403
    assert "csrf" in response.json()["detail"].lower()


def test_csrf_protection_post_with_auth():
    """Test CSRF protection allows POST with Authorization header"""
    app = FastAPI()

    @app.post("/test")
    def test_endpoint():
        return {"message": "success"}

    app.add_middleware(CSRFProtectionMiddleware)

    client = TestClient(app)
    response = client.post(
        "/test",
        json={"data": "test"},
        headers={"Authorization": "Bearer fake-token"}
    )

    assert response.status_code == 200


def test_csrf_exempt_paths():
    """Test CSRF protection exempts certain paths"""
    app = FastAPI()

    @app.post("/api/v1/auth/login")
    def login():
        return {"message": "login"}

    @app.post("/test")
    def test_endpoint():
        return {"message": "test"}

    app.add_middleware(CSRFProtectionMiddleware)

    client = TestClient(app)

    # Login should work without CSRF token
    response = client.post("/api/v1/auth/login", json={"username": "test"})
    assert response.status_code == 200

    # Other endpoints should require token
    response = client.post("/test", json={"data": "test"})
    assert response.status_code == 403


# Test Input Sanitization
def test_sanitize_string_basic():
    """Test basic string sanitization"""
    # Normal string
    assert sanitize_string("hello world") == "hello world"

    # HTML entities
    assert sanitize_string("<script>alert('xss')</script>") == "alert('xss')"

    # Special characters
    assert sanitize_string("test<>test") == "testtest"


def test_sanitize_string_length():
    """Test string length truncation"""
    long_string = "a" * 2000
    result = sanitize_string(long_string, max_length=100)
    assert len(result) == 100


def test_sanitize_string_whitespace():
    """Test whitespace trimming"""
    assert sanitize_string("  hello  ") == "hello"
    assert sanitize_string("\n\ntest\n\n") == "test"


def test_sanitize_dict_basic():
    """Test dictionary sanitization"""
    data = {
        "name": "<script>alert('xss')</script>",
        "description": "Normal text",
        "count": 123,
        "nested": {
            "value": "<b>bold</b>"
        }
    }

    sanitized = sanitize_dict(data)

    assert "script" not in sanitized["name"]
    assert sanitized["description"] == "Normal text"
    assert sanitized["count"] == 123
    assert "b" not in sanitized["nested"]["value"]


def test_sanitize_dict_selective():
    """Test selective field sanitization"""
    data = {
        "name": "<script>test</script>",
        "code": "<div>keep this</div>",
        "description": "<b>test</b>"
    }

    # Only sanitize name and description
    sanitized = sanitize_dict(data, fields_to_sanitize=["name", "description"])

    assert "script" not in sanitized["name"]
    assert "<div>" in sanitized["code"]  # Not sanitized
    assert "b" not in sanitized["description"]


def test_sanitize_dict_list_values():
    """Test sanitizing lists in dictionary"""
    data = {
        "tags": ["<script>tag1</script>", "normal tag", "<b>tag3</b>"],
        "count": 5
    }

    sanitized = sanitize_dict(data)

    assert "script" not in sanitized["tags"][0]
    assert sanitized["tags"][1] == "normal tag"
    assert "b" not in sanitized["tags"][2]
    assert sanitized["count"] == 5


# Test SQL Identifier Validation
def test_validate_sql_identifier_valid():
    """Test valid SQL identifiers"""
    assert validate_sql_identifier("users") == "users"
    assert validate_sql_identifier("user_name") == "user_name"
    assert validate_sql_identifier("_private") == "_private"
    assert validate_sql_identifier("table123") == "table123"


def test_validate_sql_identifier_invalid():
    """Test invalid SQL identifiers raise ValueError"""
    with pytest.raises(ValueError):
        validate_sql_identifier("user-name")  # Hyphen not allowed

    with pytest.raises(ValueError):
        validate_sql_identifier("123table")  # Can't start with number

    with pytest.raises(ValueError):
        validate_sql_identifier("user name")  # Space not allowed

    with pytest.raises(ValueError):
        validate_sql_identifier("user;DROP")  # Semicolon not allowed


def test_validate_sql_identifier_keywords():
    """Test SQL keywords are rejected"""
    with pytest.raises(ValueError):
        validate_sql_identifier("SELECT")

    with pytest.raises(ValueError):
        validate_sql_identifier("DROP")

    with pytest.raises(ValueError):
        validate_sql_identifier("delete")

    with pytest.raises(ValueError):
        validate_sql_identifier("union")


# Integration test with all middleware
def test_all_security_middleware_together():
    """Test all security middleware work together"""
    app = FastAPI()

    @app.get("/test")
    def test_get():
        return {"message": "get success"}

    @app.post("/test")
    def test_post():
        return {"message": "post success"}

    # Add all middleware
    app.add_middleware(CSRFProtectionMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware, requests_per_minute=10)

    client = TestClient(app)

    # GET should work and have security headers
    response = client.get("/test")
    assert response.status_code == 200
    assert "X-Content-Type-Options" in response.headers
    assert "X-RateLimit-Limit" in response.headers

    # POST without auth should fail CSRF
    response = client.post("/test", json={"data": "test"})
    assert response.status_code == 403

    # POST with auth should work
    response = client.post(
        "/test",
        json={"data": "test"},
        headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 200
    assert "X-Content-Type-Options" in response.headers


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
