# Marketplace Platform - Setup Guide

## Project Structure

The marketplace platform is organized as a microservices architecture with the following structure:

```
src/
├── api/                    # API Gateway (FastAPI)
├── services/              # Microservices
│   ├── users/            # User management service
│   ├── products/         # Product catalog service
│   ├── orders/           # Order and cart management service
│   ├── payments/         # Payment processing service
│   └── notifications/    # Notification service
└── shared/               # Shared utilities and models

tests/
├── services/             # Service-specific tests
├── test_config.py       # Testing configuration and utilities
└── conftest.py          # Pytest fixtures and configuration
```

## Dependencies

### Core Dependencies
- **FastAPI**: Web framework for building APIs
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: Database ORM
- **Uvicorn**: ASGI server

### Testing Dependencies
- **Pytest**: Testing framework
- **Hypothesis**: Property-based testing library
- **pytest-asyncio**: Async testing support
- **pytest-cov**: Coverage reporting

### Development Dependencies
- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking

## Installation

### Development Setup (Recommended)

1. **Install development dependencies** (excludes PostgreSQL for easier setup):
   ```bash
   make install-dev
   ```
   or
   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Verify setup**:
   ```bash
   make test-setup
   ```
   or
   ```bash
   python test_setup.py
   ```

### Production Setup

1. **Install production dependencies** (includes PostgreSQL):
   ```bash
   make install
   ```
   or
   ```bash
   pip install -r requirements.txt
   ```

## Testing

### Run All Tests
```bash
make test
```

### Run Tests with Coverage
```bash
make test-cov
```

### Property-Based Testing

The project uses Hypothesis for property-based testing. Test configuration is in `tests/test_config.py`:

- **Custom strategies** for domain objects (emails, passwords, prices, etc.)
- **Test data factories** for creating sample data
- **Property test utilities** for validation functions

Example property test:
```python
@given(
    email=valid_emails(),
    password=valid_passwords(),
    name=valid_names()
)
def test_user_registration_property(email, password, name):
    # Test that valid data is always accepted
    user_data = UserRegistrationData(
        email=email,
        password=password,
        first_name=name,
        last_name=name,
        role="buyer"
    )
    assert user_data.email == email
```

## Service Architecture

Each microservice follows a consistent structure:

### Service Components
- **service.py**: Core business logic and service interface
- **repository.py**: Abstract data access interface
- **config.py**: Service-specific configuration
- **__init__.py**: Public API exports

### Service Interfaces
All services implement clean interfaces with:
- **Pydantic models** for data validation
- **Abstract repositories** for data access
- **Configuration classes** for settings
- **Async/await** support for scalability

## Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/marketplace_db

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256

# Email
SMTP_HOST=smtp.gmail.com
SMTP_USERNAME=your-email@gmail.com

# Payment Gateway
PAYMENT_GATEWAY_KEY=sk_test_your_stripe_key
```

### Service-Specific Configuration
Each service has its own configuration class that can be customized via environment variables with service prefixes:

- `USER_SERVICE_*` for user service
- `PRODUCT_SERVICE_*` for product service
- `ORDER_SERVICE_*` for order service
- `PAYMENT_SERVICE_*` for payment service
- `NOTIFICATION_SERVICE_*` for notification service

## Development Workflow

### Code Quality
```bash
# Format code
make format

# Run linting
make lint

# Type checking is included in lint
```

### Testing Workflow
1. **Unit tests**: Test specific functionality
2. **Property tests**: Test universal properties with random data
3. **Integration tests**: Test service interactions

### Implementation Tasks
The implementation follows the task list in `.kiro/specs/marketplace-platform/tasks.md`:

1. ✅ **Task 1**: Project structure and dependencies (COMPLETED)
2. **Task 2**: Data models and validation
3. **Task 3**: User service implementation
4. **Task 4**: Product service implementation
5. **Task 5**: Order service implementation
6. **Task 6**: Payment service implementation
7. **Task 7**: Notification service implementation
8. **Task 8**: API Gateway and endpoints
9. **Task 9**: Database persistence
10. **Task 10**: Integration and testing

## Verification

Run the setup verification script to ensure everything is working:

```bash
python test_setup.py
```

This will verify:
- ✅ All services can be imported
- ✅ All services can be initialized
- ✅ Models can be created with valid data
- ✅ Testing framework is properly configured

## Next Steps

With the project structure and dependencies configured, you can now:

1. **Execute Task 2**: Implement data models and validation
2. **Execute Task 3**: Implement user service with authentication
3. **Continue with subsequent tasks** as defined in the implementation plan

Each task builds incrementally on the previous ones, with comprehensive testing at each step.