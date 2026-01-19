import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.utils.auth_utils import (
    validate_token,
    verify_token,
    get_current_user,
    require_scopes,
    generate_new_token,
    list_all_tokens,
)


class TestAuthUtils:
    """Test authentication utilities."""

    @pytest.mark.asyncio
    async def test_validate_token_valid(self, mock_valid_token_data):
        """Test validating a valid token."""
        with patch(
            "app.utils.auth_utils.get_token_from_db",
            new_callable=AsyncMock,
            return_value=mock_valid_token_data,
        ):
            with patch(
                "app.utils.auth_utils.update_token_usage", new_callable=AsyncMock
            ):
                result = await validate_token("mapi-test-token")
                assert result == mock_valid_token_data

    @pytest.mark.asyncio
    async def test_validate_token_invalid(self):
        """Test validating an invalid token."""
        with patch(
            "app.utils.auth_utils.get_token_from_db",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await validate_token("invalid-token")
            assert result is None

    @pytest.mark.asyncio
    async def test_validate_token_expired(self, mock_valid_token_data):
        """Test validating an expired token."""
        expired_token_data = mock_valid_token_data.copy()
        expired_token_data["expires_at"] = datetime.now() - timedelta(days=1)

        with patch(
            "app.utils.auth_utils.get_token_from_db",
            new_callable=AsyncMock,
            return_value=expired_token_data,
        ):
            result = await validate_token("expired-token")
            assert result is None

    @pytest.mark.asyncio
    async def test_validate_token_inactive(self, mock_valid_token_data):
        """Test validating an inactive token."""
        inactive_token_data = mock_valid_token_data.copy()
        inactive_token_data["is_active"] = False

        with patch(
            "app.utils.auth_utils.get_token_from_db",
            new_callable=AsyncMock,
            return_value=inactive_token_data,
        ):
            result = await validate_token("inactive-token")
            assert result is None

    @pytest.mark.asyncio
    async def test_verify_token_valid(self, mock_valid_token_data):
        """Test verifying a valid token."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="mapi-test-token"
        )

        with patch(
            "app.utils.auth_utils.validate_token",
            new_callable=AsyncMock,
            return_value=mock_valid_token_data,
        ):
            result = await verify_token(credentials)
            assert result == mock_valid_token_data

    @pytest.mark.asyncio
    async def test_verify_token_invalid(self):
        """Test verifying an invalid token."""
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="invalid-token"
        )

        with patch(
            "app.utils.auth_utils.validate_token",
            new_callable=AsyncMock,
            return_value=None,
        ):
            with pytest.raises(HTTPException) as exc_info:
                await verify_token(credentials)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user(self, mock_valid_token_data):
        """Test getting current user from token data."""
        result = await get_current_user(mock_valid_token_data)
        assert result["username"] == "test_user"
        assert result["token_id"] == "test_token_001"
        assert "read:medical_data" in result["scopes"]

    @pytest.mark.asyncio
    async def test_require_scopes_valid(self, mock_current_user):
        """Test requiring scopes with valid permissions."""
        scope_checker = require_scopes(["read:medical_data"])
        result = await scope_checker(mock_current_user)
        assert result == mock_current_user

    @pytest.mark.asyncio
    async def test_require_scopes_admin_bypass(self, mock_current_user):
        """Test admin users bypassing scope requirements."""
        admin_user = mock_current_user.copy()
        admin_user["scopes"] = ["admin"]

        scope_checker = require_scopes(["read:patient_data"])
        result = await scope_checker(admin_user)
        assert result == admin_user

    @pytest.mark.asyncio
    async def test_require_scopes_insufficient(self, mock_current_user):
        """Test requiring scopes with insufficient permissions."""
        scope_checker = require_scopes(["read:patient_data"])

        with pytest.raises(HTTPException) as exc_info:
            await scope_checker(mock_current_user)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_generate_new_token(self):
        """Test generating a new token."""
        with patch("app.utils.auth_utils.db_manager.get_connection") as mock_conn:
            mock_connection = AsyncMock()
            mock_conn.return_value.__aenter__.return_value = mock_connection
            mock_connection.fetchrow.return_value = {"token": "mapi-new-token"}

            result = await generate_new_token(
                name="Test Token",
                description="Test description",
                scopes=["read:medical_data"],
            )

            assert result == "mapi-new-token"
            assert mock_connection.fetchrow.called

    @pytest.mark.asyncio
    async def test_list_all_tokens(self):
        """Test listing all tokens."""
        # Mock data must include ALL fields that the list_all_tokens function expects
        mock_tokens = [
            {
                "token_id": "token_001",
                "name": "Token 1",
                "description": "Test token",
                "scopes": ["read:medical_data"],
                "created_at": "2024-01-01T00:00:00Z",
                "expires_at": None,
                "is_active": True,
                "username": "test_user",
                "full_name": "Test User",
                "email": "test@example.com",
                "use_count": 5,
                "last_used": "2024-01-01T12:00:00Z",
                "created_by": "admin",
                "token_preview": "mapi_abc123...",
            }
        ]

        with patch("app.utils.auth_utils.db_manager.get_connection") as mock_conn:
            mock_connection = AsyncMock()
            mock_conn.return_value.__aenter__.return_value = mock_connection
            mock_connection.fetch.return_value = mock_tokens

            result = await list_all_tokens()
            assert len(result) == 1
            assert result[0]["token_id"] == "token_001"
            assert result[0]["username"] == "test_user"
            assert result[0]["full_name"] == "Test User"
            assert result[0]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_generate_new_token_with_expiry(self):
        """Test generating a new token with expiry."""
        with patch("app.utils.auth_utils.db_manager.get_connection") as mock_conn:
            mock_connection = AsyncMock()
            mock_conn.return_value.__aenter__.return_value = mock_connection
            mock_connection.fetchrow.return_value = {"token": "mapi-expiring-token"}

            result = await generate_new_token(
                name="Expiring Token",
                description="Token with expiry",
                scopes=["read:medical_data"],
                expires_in_days=30,
            )

            assert result == "mapi-expiring-token"
            assert mock_connection.fetchrow.called

    @pytest.mark.asyncio
    async def test_database_connection_error(self):
        """Test handling database connection errors."""
        with patch(
            "app.utils.auth_utils.get_token_from_db",
            new_callable=AsyncMock,
            side_effect=Exception("Database error"),
        ):
            with pytest.raises(Exception) as exc_info:
                await validate_token("test-token")
            assert "Database error" in str(exc_info.value)
