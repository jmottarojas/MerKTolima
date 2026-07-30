"""API dependencies."""

from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any

from ..shared.auth import verify_token

# Security scheme
security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[dict]:
    """Get current user if authenticated, None otherwise."""
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    return payload


def get_services(request: Request) -> Dict[str, Any]:
    """Get all services from app state."""
    return request.app.state.services


def get_user_service(request: Request):
    """Get user service dependency."""
    return request.app.state.services["user_service"]


def get_product_service(request: Request):
    """Get product service dependency."""
    return request.app.state.services["product_service"]


def get_order_service(request: Request):
    """Get order service dependency."""
    return request.app.state.services["order_service"]


def get_payment_service(request: Request):
    """Get payment service dependency."""
    return request.app.state.services["payment_service"]


def get_notification_service(request: Request):
    """Get notification service dependency."""
    return request.app.state.services["notification_service"]


def get_search_service(request: Request):
    """Get search service dependency."""
    return request.app.state.services["search_service"]