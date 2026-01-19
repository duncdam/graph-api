from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TokenInfo(BaseModel):
    token_id: str
    name: str
    description: Optional[str] = None
    scopes: list[str] = []
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True


class TokenValidationResponse(BaseModel):
    valid: bool
    token_info: Optional[TokenInfo] = None
    user_info: Optional[dict] = None


class AuthErrorResponse(BaseModel):
    detail: str
    error_type: str


class TokenGenerateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    scopes: list[str] = []
    expires_in_days: Optional[int] = None  # None means no expiration
