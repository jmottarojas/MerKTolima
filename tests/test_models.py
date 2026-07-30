"""Property-based tests for model validation."""

import pytest
from hypothesis import given, strategies as st, assume
from decimal import Decimal
from datetime import datetime
from pydantic import ValidationError

from src.shared.models import (
    User, Product, Order, Cart, Notification,
    UserRole, ProductStatus, OrderStatus, NotificationType, PaymentStatus,
    UserProfile, UserPreferences, Address, InventoryInfo,
    CartItem, OrderItem, PaymentInfo
)


# Hypothesis strategies for generating test data
@st.composite
def valid_email_strategy(draw):
    """Generate valid email addresses with ASCII characters only."""
    username = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=ord('a'), max_codepoint=ord('z'))))
    domain = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(min_codepoint=ord('a'), max_codepoint=ord('z'))))
    tld = draw(st.sampled_from(['com', 'org', 'net', 'edu', 'gov']))
    return f"{username}@{domain}.{tld}"


@st.composite
def address_strategy(draw):
    """Generate valid Address objects."""
    return Address(
        street=draw(st.text(min_size=1, max_size=200)),
        city=draw(st.text(min_size=1, max_size=100)),
        state=draw(st.text(min_size=1, max_size=100)),
        postal_code=draw(st.text(min_size=1, max_size=20)),
        country=draw(st.text(min_size=1, max_size=100))
    )


@st.composite
def user_preferences_strategy(draw):
    """Generate valid UserPreferences objects."""
    return UserPreferences(
        email_notifications=draw(st.booleans()),
        in_app_notifications=draw(st.booleans()),
        marketing_emails=draw(st.booleans()),
        language=draw(st.text(min_size=2, max_size=5)),
        currency=draw(st.text(min_size=3, max_size=3))
    )


@st.composite
def user_profile_strategy(draw):
    """Generate valid UserProfile objects."""
    return UserProfile(
        first_name=draw(st.text(min_size=1, max_size=100)),
        last_name=draw(st.text(min_size=1, max_size=100)),
        phone=draw(st.one_of(st.none(), st.text(max_size=20))),
        address=draw(st.one_of(st.none(), address_strategy())),
        preferences=draw(user_preferences_strategy())
    )


@st.composite
def inventory_info_strategy(draw):
    """Generate valid InventoryInfo objects."""
    return InventoryInfo(
        quantity=draw(st.integers(min_value=0, max_value=10000)),
        low_stock_threshold=draw(st.integers(min_value=0, max_value=100)),
        track_inventory=draw(st.booleans())
    )


@st.composite
def valid_decimal_strategy(draw, min_value=0.01, max_value=9999.99):
    """Generate valid decimal values for prices."""
    value = draw(st.floats(min_value=min_value, max_value=max_value, allow_nan=False, allow_infinity=False))
    return Decimal(str(round(value, 2)))


@st.composite
def cart_item_strategy(draw):
    """Generate valid CartItem objects."""
    unit_price = draw(valid_decimal_strategy())
    quantity = draw(st.integers(min_value=1, max_value=100))
    total_price = unit_price * quantity
    
    return CartItem(
        product_id=draw(st.text(min_size=1, max_size=50)),
        quantity=quantity,
        unit_price=unit_price,
        total_price=total_price
    )


@st.composite
def order_item_strategy(draw):
    """Generate valid OrderItem objects."""
    unit_price = draw(valid_decimal_strategy())
    quantity = draw(st.integers(min_value=1, max_value=100))
    total_price = unit_price * quantity
    
    return OrderItem(
        product_id=draw(st.text(min_size=1, max_size=50)),
        quantity=quantity,
        unit_price=unit_price,
        total_price=total_price
    )


@st.composite
def payment_info_strategy(draw):
    """Generate valid PaymentInfo objects."""
    return PaymentInfo(
        payment_method=draw(st.text(min_size=1, max_size=50)),
        payment_status=draw(st.sampled_from(PaymentStatus)),
        transaction_id=draw(st.one_of(st.none(), st.text(min_size=1, max_size=100))),
        payment_date=draw(st.one_of(st.none(), st.datetimes())),
        amount=draw(valid_decimal_strategy()),
        currency=draw(st.text(min_size=3, max_size=3))
    )


class TestModelValidation:
    """Property-based tests for model validation."""

    @given(
        user_id=st.text(min_size=1, max_size=50),
        email=valid_email_strategy(),
        password_hash=st.text(min_size=10, max_size=100),
        role=st.sampled_from(UserRole),
        profile=user_profile_strategy()
    )
    def test_user_model_required_fields_property(self, user_id, email, password_hash, role, profile):
        """
        Property 9: Validación de campos obligatorios
        For any User with all required fields provided, the model should validate successfully.
        **Feature: marketplace-platform, Property 9: Validación de campos obligatorios**
        **Validates: Requirements 2.4**
        """
        user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            role=role,
            profile=profile
        )
        
        # All required fields are present, so validation should succeed
        assert user.id == user_id
        assert user.email is not None  # Email is processed and normalized by Pydantic
        assert "@" in user.email  # Basic email format check
        assert user.password_hash == password_hash
        assert user.role == role
        assert user.profile == profile
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    @given(
        product_id=st.text(min_size=1, max_size=50),
        seller_id=st.text(min_size=1, max_size=50),
        name=st.text(min_size=1, max_size=200),
        description=st.text(min_size=1, max_size=2000),
        price=valid_decimal_strategy(),
        category=st.text(min_size=1, max_size=100),
        inventory=inventory_info_strategy()
    )
    def test_product_model_required_fields_property(self, product_id, seller_id, name, description, price, category, inventory):
        """
        Property 9: Validación de campos obligatorios
        For any Product with all required fields provided, the model should validate successfully.
        **Feature: marketplace-platform, Property 9: Validación de campos obligatorios**
        **Validates: Requirements 2.4**
        """
        product = Product(
            id=product_id,
            seller_id=seller_id,
            name=name,
            description=description,
            price=price,
            category=category,
            inventory=inventory
        )
        
        # All required fields are present, so validation should succeed
        assert product.id == product_id
        assert product.seller_id == seller_id
        assert product.name == name
        assert product.description == description
        assert product.price == price
        assert product.category == category
        assert product.inventory == inventory
        assert isinstance(product.created_at, datetime)
        assert isinstance(product.updated_at, datetime)

    @given(
        cart_id=st.text(min_size=1, max_size=50),
        user_id=st.text(min_size=1, max_size=50),
        items=st.lists(cart_item_strategy(), min_size=0, max_size=10)
    )
    def test_cart_model_required_fields_property(self, cart_id, user_id, items):
        """
        Property 9: Validación de campos obligatorios
        For any Cart with all required fields provided, the model should validate successfully.
        **Feature: marketplace-platform, Property 9: Validación de campos obligatorios**
        **Validates: Requirements 2.4**
        """
        total_amount = sum(item.total_price for item in items)
        
        cart = Cart(
            id=cart_id,
            user_id=user_id,
            items=items,
            total_amount=total_amount
        )
        
        # All required fields are present, so validation should succeed
        assert cart.id == cart_id
        assert cart.user_id == user_id
        assert cart.items == items
        assert cart.total_amount == total_amount
        assert isinstance(cart.created_at, datetime)
        assert isinstance(cart.updated_at, datetime)

    @given(
        order_id=st.text(min_size=1, max_size=50),
        buyer_id=st.text(min_size=1, max_size=50),
        seller_id=st.text(min_size=1, max_size=50),
        items=st.lists(order_item_strategy(), min_size=1, max_size=10),
        shipping_address=address_strategy(),
        payment_info=payment_info_strategy()
    )
    def test_order_model_required_fields_property(self, order_id, buyer_id, seller_id, items, shipping_address, payment_info):
        """
        Property 9: Validación de campos obligatorios
        For any Order with all required fields provided, the model should validate successfully.
        **Feature: marketplace-platform, Property 9: Validación de campos obligatorios**
        **Validates: Requirements 2.4**
        """
        total_amount = sum(item.total_price for item in items)
        
        order = Order(
            id=order_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            items=items,
            total_amount=total_amount,
            shipping_address=shipping_address,
            payment_info=payment_info
        )
        
        # All required fields are present, so validation should succeed
        assert order.id == order_id
        assert order.buyer_id == buyer_id
        assert order.seller_id == seller_id
        assert order.items == items
        assert order.total_amount == total_amount
        assert order.shipping_address == shipping_address
        assert order.payment_info == payment_info
        assert isinstance(order.created_at, datetime)
        assert isinstance(order.updated_at, datetime)

    @given(
        notification_id=st.text(min_size=1, max_size=50),
        user_id=st.text(min_size=1, max_size=50),
        title=st.text(min_size=1, max_size=200),
        message=st.text(min_size=1, max_size=1000)
    )
    def test_notification_model_required_fields_property(self, notification_id, user_id, title, message):
        """
        Property 9: Validación de campos obligatorios
        For any Notification with all required fields provided, the model should validate successfully.
        **Feature: marketplace-platform, Property 9: Validación de campos obligatorios**
        **Validates: Requirements 2.4**
        """
        notification = Notification(
            id=notification_id,
            user_id=user_id,
            title=title,
            message=message
        )
        
        # All required fields are present, so validation should succeed
        assert notification.id == notification_id
        assert notification.user_id == user_id
        assert notification.title == title
        assert notification.message == message
        assert isinstance(notification.created_at, datetime)

    def test_missing_required_fields_validation(self):
        """Test that missing required fields raise ValidationError."""
        # Test User without required fields
        with pytest.raises(ValidationError):
            User()  # Missing all required fields
        
        with pytest.raises(ValidationError):
            User(id="test")  # Missing email, password_hash, role, profile
        
        # Test Product without required fields
        with pytest.raises(ValidationError):
            Product()  # Missing all required fields
        
        with pytest.raises(ValidationError):
            Product(id="test", seller_id="seller1")  # Missing name, description, price, category, inventory
        
        # Test Order without required fields
        with pytest.raises(ValidationError):
            Order()  # Missing all required fields
        
        # Test Notification without required fields
        with pytest.raises(ValidationError):
            Notification()  # Missing all required fields

    def test_invalid_field_values_validation(self):
        """Test that invalid field values raise ValidationError."""
        # Test invalid email
        with pytest.raises(ValidationError):
            User(
                id="test",
                email="invalid-email",  # Invalid email format
                password_hash="validhash123",
                role=UserRole.BUYER,
                profile=UserProfile(first_name="Test", last_name="User")
            )
        
        # Test negative price
        with pytest.raises(ValidationError):
            Product(
                id="test",
                seller_id="seller1",
                name="Test Product",
                description="Test Description",
                price=Decimal("-10.00"),  # Negative price
                category="Test Category",
                inventory=InventoryInfo(quantity=10)
            )
        
        # Test negative inventory quantity
        with pytest.raises(ValidationError):
            InventoryInfo(quantity=-5)  # Negative quantity
        
        # Test zero quantity in cart item
        with pytest.raises(ValidationError):
            CartItem(
                product_id="test",
                quantity=0,  # Zero quantity
                unit_price=Decimal("10.00"),
                total_price=Decimal("0.00")
            )