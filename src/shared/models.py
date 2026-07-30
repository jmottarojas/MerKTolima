"""Base models and common data structures."""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from decimal import Decimal


class UserRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"


class NotificationType(str, Enum):
    EMAIL = "email"
    IN_APP = "in_app"
    BOTH = "both"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


# Base Models
class BaseResponse(BaseModel):
    """Base response model."""
    success: bool
    message: str


class ErrorResponse(BaseResponse):
    """Error response model."""
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[dict] = None


# Address Model
class Address(BaseModel):
    """Address model for shipping and billing."""
    street: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(..., min_length=1, max_length=100)


# User Models
class UserPreferences(BaseModel):
    """User notification and display preferences."""
    email_notifications: bool = True
    in_app_notifications: bool = True
    marketing_emails: bool = False
    language: str = Field(default="es", min_length=2, max_length=5)
    currency: str = Field(default="USD", min_length=3, max_length=3)


class UserProfile(BaseModel):
    """User profile information."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[Address] = None
    preferences: UserPreferences = Field(default_factory=UserPreferences)


class User(BaseModel):
    """User model for buyers and sellers."""
    id: str = Field(..., min_length=1)
    email: EmailStr
    password_hash: str = Field(..., min_length=1)
    role: UserRole
    profile: UserProfile
    is_active: bool = True
    email_verified: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('password_hash')
    def validate_password_hash(cls, v):
        if len(v) < 10:  # Basic validation for hashed password
            raise ValueError('Password hash must be at least 10 characters')
        return v


# Product Models
class InventoryInfo(BaseModel):
    """Product inventory information."""
    quantity: int = Field(..., ge=0)
    low_stock_threshold: int = Field(default=10, ge=0)
    track_inventory: bool = True

    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('Quantity cannot be negative')
        return v


class Product(BaseModel):
    """Product model for marketplace items."""
    id: str = Field(..., min_length=1)
    seller_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    price: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    category: str = Field(..., min_length=1, max_length=100)
    images: List[str] = Field(default_factory=list)
    inventory: InventoryInfo
    status: ProductStatus = ProductStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v

    @validator('images')
    def validate_images(cls, v):
        if len(v) > 10:  # Limit number of images
            raise ValueError('Maximum 10 images allowed')
        return v


# Cart Models
class CartItem(BaseModel):
    """Individual item in shopping cart."""
    product_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0, decimal_places=2)
    total_price: Decimal = Field(..., gt=0, decimal_places=2)

    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v

    @validator('total_price')
    def validate_total_price(cls, v, values):
        if 'unit_price' in values and 'quantity' in values:
            expected_total = values['unit_price'] * values['quantity']
            if abs(v - expected_total) > Decimal('0.01'):
                raise ValueError('Total price must equal unit_price * quantity')
        return v


class Cart(BaseModel):
    """Shopping cart model."""
    id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    items: List[CartItem] = Field(default_factory=list)
    total_amount: Decimal = Field(default=Decimal('0.00'), ge=0, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('total_amount')
    def validate_total_amount(cls, v, values):
        if 'items' in values:
            expected_total = sum(item.total_price for item in values['items'])
            if abs(v - expected_total) > Decimal('0.01'):
                raise ValueError('Total amount must equal sum of item totals')
        return v


# Order Models
class OrderItem(BaseModel):
    """Individual item in an order."""
    product_id: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0)
    unit_price: Decimal = Field(..., gt=0, decimal_places=2)
    total_price: Decimal = Field(..., gt=0, decimal_places=2)

    @validator('total_price')
    def validate_total_price(cls, v, values):
        if 'unit_price' in values and 'quantity' in values:
            expected_total = values['unit_price'] * values['quantity']
            if abs(v - expected_total) > Decimal('0.01'):
                raise ValueError('Total price must equal unit_price * quantity')
        return v


class PaymentInfo(BaseModel):
    """Payment information for orders."""
    payment_method: str = Field(..., min_length=1)
    payment_status: PaymentStatus = PaymentStatus.PENDING
    transaction_id: Optional[str] = None
    payment_date: Optional[datetime] = None
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)


class Order(BaseModel):
    """Order model for completed purchases."""
    id: str = Field(..., min_length=1)
    buyer_id: str = Field(..., min_length=1)
    seller_id: str = Field(..., min_length=1)
    items: List[OrderItem] = Field(..., min_items=1)
    total_amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    status: OrderStatus = OrderStatus.PENDING
    shipping_address: Address
    payment_info: PaymentInfo
    tracking_number: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Order must have at least one item')
        return v

    @validator('total_amount')
    def validate_total_amount(cls, v, values):
        if 'items' in values:
            expected_total = sum(item.total_price for item in values['items'])
            if abs(v - expected_total) > Decimal('0.01'):
                raise ValueError('Total amount must equal sum of item totals')
        return v

    @validator('tracking_number')
    def validate_tracking_number(cls, v, values):
        if v and 'status' in values:
            if values['status'] in [OrderStatus.SHIPPED, OrderStatus.DELIVERED] and not v:
                raise ValueError('Tracking number required for shipped/delivered orders')
        return v


# Notification Models
class Notification(BaseModel):
    """Notification model for user communications."""
    id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=1000)
    notification_type: NotificationType = NotificationType.IN_APP
    is_read: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    read_at: Optional[datetime] = None

    @validator('read_at')
    def validate_read_at(cls, v, values):
        if v and 'is_read' in values and not values['is_read']:
            raise ValueError('read_at should only be set when is_read is True')
        return v


class SearchResults(BaseModel):
    """Search results model."""
    products: List["Product"]
    total_count: int
    page: int
    page_size: int
    total_pages: int = Field(default=0)