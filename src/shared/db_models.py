"""SQLAlchemy database models for the marketplace platform."""

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text, 
    Numeric, ForeignKey, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .models import UserRole, OrderStatus, ProductStatus, NotificationType, PaymentStatus

Base = declarative_base()


class UserDB(Base):
    """SQLAlchemy User model."""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    
    # Profile information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Address information (stored as JSON for flexibility)
    address = Column(JSON, nullable=True)
    
    # User preferences (stored as JSON)
    preferences = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    products = relationship("ProductDB", back_populates="seller", cascade="all, delete-orphan")
    buyer_orders = relationship("OrderDB", foreign_keys="OrderDB.buyer_id", back_populates="buyer")
    seller_orders = relationship("OrderDB", foreign_keys="OrderDB.seller_id", back_populates="seller")
    carts = relationship("CartDB", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("NotificationDB", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_role', 'role'),
        Index('idx_users_created_at', 'created_at'),
    )


class ProductDB(Base):
    """SQLAlchemy Product model."""
    __tablename__ = "products"
    
    id = Column(String(36), primary_key=True)
    seller_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    category = Column(String(100), nullable=False)
    images = Column(JSON, nullable=True)  # List of image URLs
    
    # Inventory information
    inventory_quantity = Column(Integer, default=0, nullable=False)
    low_stock_threshold = Column(Integer, default=10, nullable=False)
    track_inventory = Column(Boolean, default=True, nullable=False)
    
    status = Column(SQLEnum(ProductStatus), default=ProductStatus.ACTIVE, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    seller = relationship("UserDB", back_populates="products")
    cart_items = relationship("CartItemDB", back_populates="product")
    order_items = relationship("OrderItemDB", back_populates="product")
    
    # Indexes
    __table_args__ = (
        Index('idx_products_seller_id', 'seller_id'),
        Index('idx_products_category', 'category'),
        Index('idx_products_status', 'status'),
        Index('idx_products_price', 'price'),
        Index('idx_products_created_at', 'created_at'),
        Index('idx_products_name_search', 'name'),
    )


class CartDB(Base):
    """SQLAlchemy Cart model."""
    __tablename__ = "carts"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    total_amount = Column(Numeric(10, 2), default=0.00, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("UserDB", back_populates="carts")
    items = relationship("CartItemDB", back_populates="cart", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_carts_user_id', 'user_id'),
        Index('idx_carts_updated_at', 'updated_at'),
    )


class CartItemDB(Base):
    """SQLAlchemy CartItem model."""
    __tablename__ = "cart_items"
    
    id = Column(String(36), primary_key=True)
    cart_id = Column(String(36), ForeignKey("carts.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    cart = relationship("CartDB", back_populates="items")
    product = relationship("ProductDB", back_populates="cart_items")
    
    # Indexes
    __table_args__ = (
        Index('idx_cart_items_cart_id', 'cart_id'),
        Index('idx_cart_items_product_id', 'product_id'),
    )


class OrderDB(Base):
    """SQLAlchemy Order model."""
    __tablename__ = "orders"
    
    id = Column(String(36), primary_key=True)
    buyer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    seller_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    
    # Shipping information (stored as JSON)
    shipping_address = Column(JSON, nullable=False)
    
    # Payment information (stored as JSON)
    payment_info = Column(JSON, nullable=False)
    
    tracking_number = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    buyer = relationship("UserDB", foreign_keys=[buyer_id], back_populates="buyer_orders")
    seller = relationship("UserDB", foreign_keys=[seller_id], back_populates="seller_orders")
    items = relationship("OrderItemDB", back_populates="order", cascade="all, delete-orphan")
    payments = relationship("PaymentDB", back_populates="order", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_orders_buyer_id', 'buyer_id'),
        Index('idx_orders_seller_id', 'seller_id'),
        Index('idx_orders_status', 'status'),
        Index('idx_orders_created_at', 'created_at'),
        Index('idx_orders_tracking_number', 'tracking_number'),
    )


class OrderItemDB(Base):
    """SQLAlchemy OrderItem model."""
    __tablename__ = "order_items"
    
    id = Column(String(36), primary_key=True)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    order = relationship("OrderDB", back_populates="items")
    product = relationship("ProductDB", back_populates="order_items")
    
    # Indexes
    __table_args__ = (
        Index('idx_order_items_order_id', 'order_id'),
        Index('idx_order_items_product_id', 'product_id'),
    )


class PaymentDB(Base):
    """SQLAlchemy Payment model."""
    __tablename__ = "payments"
    
    id = Column(String(36), primary_key=True)
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    payment_method = Column(String(50), nullable=False)
    payment_status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    transaction_id = Column(String(100), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Payment processor response (stored as JSON)
    processor_response = Column(JSON, nullable=True)
    
    # Encrypted payment details (stored as JSON)
    encrypted_details = Column(JSON, nullable=True)
    
    # Timestamps
    payment_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    order = relationship("OrderDB", back_populates="payments")
    receipts = relationship("ReceiptDB", back_populates="payment", cascade="all, delete-orphan")
    refunds = relationship("RefundDB", back_populates="payment", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_payments_order_id', 'order_id'),
        Index('idx_payments_status', 'payment_status'),
        Index('idx_payments_transaction_id', 'transaction_id'),
        Index('idx_payments_created_at', 'created_at'),
    )


class ReceiptDB(Base):
    """SQLAlchemy Receipt model."""
    __tablename__ = "receipts"
    
    id = Column(String(36), primary_key=True)
    payment_id = Column(String(36), ForeignKey("payments.id"), nullable=False)
    receipt_number = Column(String(50), unique=True, nullable=False)
    receipt_data = Column(JSON, nullable=False)  # Complete receipt information
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    payment = relationship("PaymentDB", back_populates="receipts")
    
    # Indexes
    __table_args__ = (
        Index('idx_receipts_payment_id', 'payment_id'),
        Index('idx_receipts_receipt_number', 'receipt_number'),
    )


class RefundDB(Base):
    """SQLAlchemy Refund model."""
    __tablename__ = "refunds"
    
    id = Column(String(36), primary_key=True)
    payment_id = Column(String(36), ForeignKey("payments.id"), nullable=False)
    refund_amount = Column(Numeric(10, 2), nullable=False)
    reason = Column(String(500), nullable=True)
    status = Column(String(20), default="pending", nullable=False)
    transaction_id = Column(String(100), nullable=True)
    
    # Processor response (stored as JSON)
    processor_response = Column(JSON, nullable=True)
    
    # Timestamps
    refund_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    payment = relationship("PaymentDB", back_populates="refunds")
    
    # Indexes
    __table_args__ = (
        Index('idx_refunds_payment_id', 'payment_id'),
        Index('idx_refunds_status', 'status'),
        Index('idx_refunds_created_at', 'created_at'),
    )


class NotificationDB(Base):
    """SQLAlchemy Notification model."""
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(String(1000), nullable=False)
    notification_type = Column(SQLEnum(NotificationType), default=NotificationType.IN_APP, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    
    # Additional notification metadata (stored as JSON)
    notification_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("UserDB", back_populates="notifications")
    
    # Indexes
    __table_args__ = (
        Index('idx_notifications_user_id', 'user_id'),
        Index('idx_notifications_is_read', 'is_read'),
        Index('idx_notifications_type', 'notification_type'),
        Index('idx_notifications_created_at', 'created_at'),
    )


class NotificationPreferencesDB(Base):
    """SQLAlchemy NotificationPreferences model."""
    __tablename__ = "notification_preferences"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Preference settings (stored as JSON for flexibility)
    preferences = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_notification_preferences_user_id', 'user_id'),
    )