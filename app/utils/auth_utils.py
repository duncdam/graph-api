import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.database import db_manager
from app.utils.app_utils import logger

# Security scheme
security = HTTPBearer()


async def get_token_from_db(token: str) -> Optional[Dict]:
    """Get token data from PostgreSQL database"""
    async with db_manager.get_connection() as conn:
        try:
            query = """
                SELECT token, token_id, name, description, scopes, created_at, 
                       expires_at, is_active, username, full_name, email,
                       use_count, last_used
                FROM graph.access_tokens 
                WHERE token = $1
            """
            row = await conn.fetchrow(query, token)

            if not row:
                return None

            return {
                "token": row["token"],
                "token_id": row["token_id"],
                "name": row["name"],
                "description": row["description"],
                "scopes": row["scopes"] or [],
                "created_at": row["created_at"],
                "expires_at": row["expires_at"],
                "is_active": row["is_active"],
                "user_info": {
                    "username": row["username"],
                    "full_name": row["full_name"],
                    "email": row["email"],
                },
                "use_count": row["use_count"],
                "last_used": row["last_used"],
            }
        except Exception as e:
            logger.exception(f"Database error getting token: {str(e)}")
            return None


async def update_token_usage(token: str):
    """Update token usage statistics"""
    async with db_manager.get_connection() as conn:
        try:
            query = """
                UPDATE graph.access_tokens 
                SET use_count = use_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE token = $1
            """
            await conn.execute(query, token)
        except Exception as e:
            logger.exception(f"Error updating token usage: {str(e)}")


async def validate_token(token: str) -> Optional[Dict]:
    """Validate a pre-generated access token from database"""
    # Remove 'Bearer ' prefix if present
    if token.startswith("Bearer "):
        token = token[7:]

    # Get token from database
    token_data = await get_token_from_db(token)

    if not token_data:
        return None

    # Check if token is active
    if not token_data.get("is_active", False):
        return None

    # Check if token has expired
    expires_at = token_data.get("expires_at")
    if expires_at and datetime.now(expires_at.tzinfo) > expires_at:
        return None

    # Update usage statistics
    await update_token_usage(token)

    return token_data


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict:
    """Verify access token and return token data"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        token_data = await validate_token(token)

        if token_data is None:
            raise credentials_exception

        return token_data

    except Exception:
        raise credentials_exception


async def get_current_user(token_data: Dict = Depends(verify_token)) -> Dict:
    """Get current user from token data"""
    user_info = token_data.get("user_info", {})

    # Combine token info with user info
    return {
        **user_info,
        "token_id": token_data.get("token_id"),
        "scopes": token_data.get("scopes", []),
        "token_name": token_data.get("name"),
        "use_count": token_data.get("use_count", 0),
        "last_used": token_data.get("last_used"),
    }


def require_scopes(required_scopes: List[str]):
    """Dependency to require specific scopes"""

    async def check_scopes(current_user: Dict = Depends(get_current_user)):
        user_scopes = current_user.get("scopes", [])

        # Admin users have access to everything
        if "admin" in user_scopes:
            return current_user

        # Check if user has required scopes
        for scope in required_scopes:
            if scope not in user_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Not enough permissions. Required scope: {scope}",
                )
        return current_user

    return check_scopes


# Common scope dependencies
def require_read_medical_data(
    current_user: Dict = Depends(require_scopes(["read:medical_data"])),
):
    return current_user


def require_read_patient_data(
    current_user: Dict = Depends(require_scopes(["read:patient_data"])),
):
    return current_user


def require_admin(current_user: Dict = Depends(require_scopes(["admin"]))):
    return current_user


async def generate_new_token(
    name: str,
    description: str = None,
    scopes: List[str] = None,
    expires_in_days: int = None,
    username: str = None,
    full_name: str = None,
    email: str = None,
    created_by: str = None,
) -> str:
    """Generate a new access token and save to database"""
    if scopes is None:
        scopes = ["read:medical_data"]

    # Generate a secure random token
    token_suffix = secrets.token_urlsafe(32)
    new_token = f"mapi_{token_suffix}"

    # Generate unique token_id
    token_id_suffix = secrets.token_urlsafe(8)
    token_id = f"token_{token_id_suffix}"

    # Calculate expiration
    expires_at = None
    if expires_in_days:
        expires_at = datetime.now() + timedelta(days=expires_in_days)

    # Default user info
    if not username:
        username = f"user_{token_id_suffix}"
    if not full_name:
        full_name = f"Token User - {name}"
    if not email:
        email = "generated@medical-api.com"

    async with db_manager.get_connection() as conn:
        try:
            query = """
                INSERT INTO graph.access_tokens 
                (token, token_id, name, description, scopes, expires_at, 
                 username, full_name, email, created_by)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING token
            """
            result = await conn.fetchrow(
                query,
                new_token,
                token_id,
                name,
                description,
                scopes,
                expires_at,
                username,
                full_name,
                email,
                created_by,
            )
            return result["token"]
        except Exception as e:
            raise Exception(f"Failed to create token: {str(e)}")


async def list_all_tokens() -> List[Dict]:
    """List all tokens from database"""
    async with db_manager.get_connection() as conn:
        try:
            query = """
                SELECT token_id, name, description, scopes, created_at, 
                       expires_at, is_active, username, full_name, email,
                       use_count, last_used, created_by,
                       LEFT(token, 10) || '...' as token_preview
                FROM graph.access_tokens 
                ORDER BY created_at DESC
            """
            rows = await conn.fetch(query)

            return [
                {
                    "token_id": row["token_id"],
                    "name": row["name"],
                    "description": row["description"],
                    "scopes": row["scopes"],
                    "created_at": row["created_at"],
                    "expires_at": row["expires_at"],
                    "is_active": row["is_active"],
                    "username": row["username"],
                    "full_name": row["full_name"],
                    "email": row["email"],
                    "use_count": row["use_count"],
                    "last_used": row["last_used"],
                    "created_by": row["created_by"],
                    "token_preview": row["token_preview"],
                }
                for row in rows
            ]
        except Exception as e:
            logger.exception(f"Database error listing tokens: {str(e)}")
            return []


async def deactivate_token(token_id: str) -> bool:
    """Deactivate a token by token_id"""
    async with db_manager.get_connection() as conn:
        try:
            query = """
                UPDATE graph.access_tokens 
                SET is_active = FALSE 
                WHERE token_id = $1
                RETURNING token_id
            """
            result = await conn.fetchrow(query, token_id)
            return result is not None
        except Exception as e:
            logger.exception(f"Database error deactivating token: {str(e)}")
            return False


async def activate_token(token_id: str) -> bool:
    """Activate a token by token_id"""
    async with db_manager.get_connection() as conn:
        try:
            query = """
                UPDATE graph.access_tokens 
                SET is_active = TRUE 
                WHERE token_id = $1
                RETURNING token_id
            """
            result = await conn.fetchrow(query, token_id)
            return result is not None
        except Exception as e:
            logger.exception(f"Database error activating token: {str(e)}")
            return False


async def delete_token(token_id: str) -> bool:
    """Permanently delete a token by token_id"""
    async with db_manager.get_connection() as conn:
        try:
            query = """
                DELETE FROM graph.access_tokens 
                WHERE token_id = $1
                RETURNING token_id
            """
            result = await conn.fetchrow(query, token_id)
            return result is not None
        except Exception as e:
            logger.exception(f"Database error deleting token: {str(e)}")
            return False
