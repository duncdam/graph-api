from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, List
from app.models.auth_schemas import (
    TokenInfo,
    TokenValidationResponse,
    TokenGenerateRequest,
)
from app.utils.auth_utils import (
    validate_token,
    get_current_user,
    require_admin,
    generate_new_token,
    list_all_tokens,
)

router = APIRouter()


@router.post(
    "/validate",
    response_model=TokenValidationResponse,
    summary="Validate Access Token",
    description="Validate an access token and return token information",
)
async def validate_access_token(token: str):
    """
    Validate an access token and return its information
    """
    token_data = await validate_token(token)

    if token_data is None:
        return TokenValidationResponse(valid=False, token_info=None, user_info=None)

    return TokenValidationResponse(
        valid=True,
        token_info=TokenInfo(
            token_id=token_data["token_id"],
            name=token_data["name"],
            description=token_data.get("description"),
            scopes=token_data["scopes"],
            created_at=token_data["created_at"],
            expires_at=token_data.get("expires_at"),
            is_active=token_data["is_active"],
        ),
        user_info=token_data.get("user_info"),
    )


@router.get(
    "/me",
    summary="Get Current Token Info",
    description="Get information about the currently used token",
)
async def get_current_token_info(current_user: Dict = Depends(get_current_user)):
    """
    Get current token information
    """
    return {
        "username": current_user["username"],
        "full_name": current_user.get("full_name"),
        "email": current_user.get("email"),
        "token_id": current_user.get("token_id"),
        "token_name": current_user.get("token_name"),
        "scopes": current_user.get("scopes", []),
        "authenticated": True,
    }


@router.get(
    "/tokens",
    summary="List All Tokens (Admin Only)",
    description="List all access tokens and their information",
)
async def list_tokens(current_user: Dict = Depends(require_admin)):
    """
    List all access tokens (Admin only)
    """
    tokens = await list_all_tokens()
    token_list = []

    for token in tokens:
        # Don't expose the actual token in the list for security
        token_info = {
            "token_id": token["token_id"],
            "name": token["name"],
            "description": token.get("description"),
            "scopes": token["scopes"],
            "created_at": token["created_at"],
            "expires_at": token.get("expires_at"),
            "is_active": token["is_active"],
            "token_preview": f"{token['token_id'][:10]}...",  # Show only first 10 chars
        }
        token_list.append(token_info)

    return {"tokens": token_list, "count": len(token_list)}


@router.get(
    "/test-auth",
    summary="Test Authentication",
    description="Test endpoint to verify token authentication is working",
)
async def test_auth(current_user: Dict = Depends(get_current_user)):
    """
    Test endpoint for token authentication
    """
    return {
        "message": f"Hello {current_user['username']}!",
        "token_name": current_user.get("token_name"),
        "user_scopes": current_user.get("scopes", []),
        "authenticated": True,
        "token_id": current_user.get("token_id"),
    }
