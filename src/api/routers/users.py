"""User endpoints."""

from fastapi import APIRouter, HTTPException, Depends, status, Request
from typing import Optional
from pydantic import BaseModel

from ...services.users.service import UserService, UserRegistrationData, LoginCredentials, UserProfileUpdates, User, AuthToken, UserRegistrationError, AuthenticationError
from ...shared.models import BaseResponse
from ..dependencies import get_current_user, get_current_user_optional

router = APIRouter(tags=["users"])


def get_user_service(request):
    """Get user service from app state."""
    return request.app.state.services["user_service"]


class UserRegistrationRequest(BaseModel):
    """User registration request model."""
    email: str
    password: str
    first_name: str
    last_name: str
    role: str = "buyer"


class LoginRequest(BaseModel):
    """Login request model."""
    email: str
    password: str


class UserProfileUpdateRequest(BaseModel):
    """User profile update request model."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


class UserResponse(BaseModel):
    """User response model."""
    id: str
    email: str
    role: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    created_at: str
    updated_at: str


@router.post("/register", response_model=UserResponse)
async def register_user(registration_request: UserRegistrationRequest, request: Request):
    """Register a new user."""
    try:
        user_service = request.app.state.services["user_service"]
        
        user_data = UserRegistrationData(
            email=registration_request.email,
            password=registration_request.password,
            first_name=registration_request.first_name,
            last_name=registration_request.last_name,
            role=registration_request.role
        )
        
        user = await user_service.register_user(user_data)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
        
    except UserRegistrationError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=AuthToken)
async def login_user(login_request: LoginRequest, request: Request):
    """Authenticate user and return token."""
    import logging
    logger = logging.getLogger(__name__)
    
    # Add debug at the very beginning
    print("🔥 LOGIN ENDPOINT CALLED!")
    logger.info("🔥 LOGIN ENDPOINT CALLED!")
    
    try:
        logger.info(f"DEBUG: Login attempt for email: {login_request.email}")
        print(f"DEBUG: Login attempt for email: {login_request.email}")
        
        user_service = request.app.state.services["user_service"]
        logger.info(f"DEBUG: Got user service: {type(user_service)}")
        print(f"DEBUG: Got user service: {type(user_service)}")
        
        # Check if user exists first
        user = await user_service.get_user_by_email(login_request.email)
        if user:
            logger.info(f"DEBUG: User found: {user.email}")
            print(f"DEBUG: User found: {user.email}")
        else:
            logger.info(f"DEBUG: User not found for email: {login_request.email}")
            print(f"DEBUG: User not found for email: {login_request.email}")
        
        credentials = LoginCredentials(
            email=login_request.email,
            password=login_request.password
        )
        
        logger.info(f"DEBUG: Created credentials for: {credentials.email}")
        print(f"DEBUG: Created credentials for: {credentials.email}")
        
        token = await user_service.authenticate_user(credentials)
        logger.info(f"DEBUG: Authentication successful, token created")
        print(f"DEBUG: Authentication successful, token created")
        
        return token
        
    except AuthenticationError as e:
        logger.error(f"DEBUG: Authentication error: {e}")
        print(f"DEBUG: Authentication error: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    except ValueError as e:
        logger.error(f"DEBUG: Value error: {e}")
        print(f"DEBUG: Value error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"DEBUG: Unexpected error: {e}")
        print(f"DEBUG: Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(request: Request, current_user: dict = Depends(get_current_user)):
    """Get current user's profile."""
    user_service = request.app.state.services["user_service"]
    user = await user_service.get_user_by_id(current_user["sub"])
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_request: UserProfileUpdateRequest,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Update current user's profile."""
    try:
        user_service = request.app.state.services["user_service"]
        
        updates = UserProfileUpdates(
            first_name=profile_request.first_name,
            last_name=profile_request.last_name,
            phone=profile_request.phone
        )
        
        user = await user_service.update_user_profile(current_user["sub"], updates)
        
        return UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: str,
    request: Request,
    current_user: Optional[dict] = Depends(get_current_user_optional)
):
    """Get user by ID (public endpoint with optional authentication)."""
    user_service = request.app.state.services["user_service"]
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone if current_user and current_user["sub"] == user_id else None,  # Only show phone to owner
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat()
    )