"""Tests for security utilities: password hashing and JWT tokens."""

from congo_brain.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_password_returns_string(self) -> None:
        hashed = hash_password("testpassword")
        assert isinstance(hashed, str)

    def test_hash_password_is_not_plaintext(self) -> None:
        hashed = hash_password("testpassword")
        assert hashed != "testpassword"

    def test_verify_correct_password(self) -> None:
        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True

    def test_verify_wrong_password(self) -> None:
        hashed = hash_password("mypassword")
        assert verify_password("wrongpassword", hashed) is False

    def test_same_password_produces_different_hashes(self) -> None:
        h1 = hash_password("samepass")
        h2 = hash_password("samepass")
        assert h1 != h2  # bcrypt uses random salt

    def test_empty_password(self) -> None:
        hashed = hash_password("")
        assert verify_password("", hashed) is True


class TestJWT:
    def test_create_and_decode_token(self) -> None:
        token = create_access_token({"sub": "testuser", "role": "admin"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["role"] == "admin"
        assert "exp" in payload

    def test_decode_invalid_token(self) -> None:
        payload = decode_access_token("invalid.token.here")
        assert payload is None

    def test_decode_tampered_token(self) -> None:
        token = create_access_token({"sub": "testuser"})
        tampered = token[:-5] + "XXXXX"
        payload = decode_access_token(tampered)
        assert payload is None

    def test_token_contains_expiry(self) -> None:
        from datetime import timedelta

        token = create_access_token({"sub": "u"}, expires_delta=timedelta(minutes=30))
        payload = decode_access_token(token)
        assert payload is not None
        assert "exp" in payload
