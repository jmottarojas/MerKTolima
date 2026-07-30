"""API Gateway - Main FastAPI application."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from dotenv import load_dotenv

from ..shared.models import ErrorResponse
from ..shared.service_factory import initialize_services
from ..shared.service_integration import orchestrator
from .routers import users, products, orders, payments, notifications

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="Marketplace Platform API",
    description="API Gateway para la plataforma de marketplace",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _seed_test_users(user_service):
    """Seed test users into the in-memory store on startup."""
    from ..services.users.service import UserRegistrationData, UserRegistrationError

    test_users = [
        {"email": "buyer@test.com", "password": "Password123", "first_name": "Juan", "last_name": "Comprador", "role": "buyer"},
        {"email": "seller@test.com", "password": "Password123", "first_name": "Maria", "last_name": "Vendedora", "role": "seller"},
        {"email": "admin@merkatolima.com", "password": "Admin123", "first_name": "Admin", "last_name": "Sistema", "role": "seller"},
        {"email": "vendedor@merkatolima.com", "password": "Vendedor123", "first_name": "Carlos", "last_name": "Vendedor", "role": "seller"},
        {"email": "comprador@merkatolima.com", "password": "Comprador123", "first_name": "Ana", "last_name": "Compradora", "role": "buyer"},
    ]

    for u in test_users:
        try:
            await user_service.register_user(UserRegistrationData(**u))
            print(f"✅ STARTUP: Test user created: {u['email']}")
        except (UserRegistrationError, Exception) as e:
            print(f"⚠️ STARTUP: Could not create {u['email']}: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Initializing marketplace platform services...")
    print("🚀 STARTUP: Initializing marketplace platform services...")
    
    # Initialize database if using database
    use_database = os.getenv("USE_DATABASE", "False").lower() == "true"
    db_session = None
    
    if use_database:
        from ..shared.database import create_tables, get_db_session
        # Create tables if they don't exist
        create_tables()
        # Get database session
        db_session = get_db_session()
        logger.info("Database initialized and tables created")
        print("🗄️ STARTUP: Database initialized and tables created")
    
    # Initialize all services
    services = initialize_services(use_database=use_database, db_session=db_session)
    
    # Store services in app state for access by routers
    app.state.services = services
    
    # Seed test users into the running in-memory store
    await _seed_test_users(services.get("user_service"))

    logger.info("Marketplace platform startup complete")
    print("✅ STARTUP: Marketplace platform startup complete")
    print(f"📋 STARTUP: Available services: {list(services.keys())}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down marketplace platform...")


# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with consistent error format."""
    print(f"🚨 HTTP EXCEPTION HANDLER: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=exc.detail,
            error_code=f"HTTP_{exc.status_code}"
        ).dict()
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    print(f"🚨 VALUE ERROR HANDLER: {exc}")
    return JSONResponse(
        status_code=400,
        content=ErrorResponse(
            message=str(exc),
            error_code="VALIDATION_ERROR"
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details={"error": str(exc)} if os.getenv("DEBUG", "False").lower() == "true" else None
        ).dict()
    )


# Include routers
print("🔧 DEBUG: Including routers...")
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
print("✅ DEBUG: Users router included")
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
print("✅ DEBUG: Products router included")
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
print("✅ DEBUG: Orders router included")
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
print("✅ DEBUG: Payments router included")
app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["notifications"])
print("✅ DEBUG: Notifications router included")
print("🎉 DEBUG: All routers included successfully!")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Marketplace Platform API Gateway", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "api-gateway"}


@app.get("/api/v1")
async def api_info():
    """API information endpoint."""
    return {
        "name": "Marketplace Platform API",
        "version": "1.0.0",
        "description": "REST API for marketplace platform",
        "endpoints": {
            "users": "/api/v1/users",
            "products": "/api/v1/products", 
            "orders": "/api/v1/orders",
            "payments": "/api/v1/payments",
            "notifications": "/api/v1/notifications"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )