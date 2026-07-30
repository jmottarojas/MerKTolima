"""Order and cart endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel
from decimal import Decimal

from ...services.orders.service import OrderService
from ...services.products.service import ProductService
from ...services.payments.service import PaymentService, PaymentMethod, PaymentMethodType
from ...services.orders.repository import InMemoryOrderRepository
from ...shared.models import Address, OrderStatus, BaseResponse
from ..dependencies import get_current_user

router = APIRouter(tags=["orders"])

# Initialize services
order_repository = InMemoryOrderRepository()
product_service = ProductService()
payment_service = PaymentService()
order_service = OrderService(order_repository, product_service, payment_service)


class AddToCartRequest(BaseModel):
    """Add to cart request model."""
    product_id: str
    quantity: int


class UpdateCartItemRequest(BaseModel):
    """Update cart item request model."""
    quantity: int


class AddressRequest(BaseModel):
    """Address request model."""
    street: str
    city: str
    state: str
    postal_code: Optional[str] = None
    country: str


class CreateOrderRequest(BaseModel):
    """Create order request model."""
    cart_id: str
    shipping_address: AddressRequest
    payment_method: str  # Simplified for API


class CartItemResponse(BaseModel):
    """Cart item response model."""
    product_id: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class CartResponse(BaseModel):
    """Cart response model."""
    id: str
    user_id: str
    items: List[CartItemResponse]
    total_amount: Decimal
    currency: str
    created_at: str
    updated_at: str


class OrderItemResponse(BaseModel):
    """Order item response model."""
    product_id: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal


class PaymentInfoResponse(BaseModel):
    """Payment info response model."""
    payment_method: str
    payment_status: str
    transaction_id: Optional[str] = None
    payment_date: Optional[str] = None
    amount: Decimal
    currency: str


class OrderResponse(BaseModel):
    """Order response model."""
    id: str
    buyer_id: str
    seller_id: str
    items: List[OrderItemResponse]
    total_amount: Decimal
    currency: str
    status: str
    shipping_address: AddressRequest
    payment_info: PaymentInfoResponse
    tracking_number: Optional[str] = None
    created_at: str
    updated_at: str


# Cart endpoints
@router.post("/cart/items", response_model=CartResponse)
async def add_to_cart(
    request: AddToCartRequest,
    current_user: dict = Depends(get_current_user)
):
    """Add item to cart."""
    try:
        cart = await order_service.add_to_cart(
            current_user["sub"],
            request.product_id,
            request.quantity
        )
        
        return CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            items=[
                CartItemResponse(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price
                )
                for item in cart.items
            ],
            total_amount=cart.total_amount,
            currency=cart.currency,
            created_at=cart.created_at.isoformat(),
            updated_at=cart.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/cart", response_model=Optional[CartResponse])
async def get_cart(current_user: dict = Depends(get_current_user)):
    """Get user's cart."""
    cart = await order_service.get_cart(current_user["sub"])
    
    if not cart:
        return None
    
    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=[
            CartItemResponse(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price
            )
            for item in cart.items
        ],
        total_amount=cart.total_amount,
        currency=cart.currency,
        created_at=cart.created_at.isoformat(),
        updated_at=cart.updated_at.isoformat()
    )


@router.put("/cart/items/{product_id}", response_model=CartResponse)
async def update_cart_item(
    product_id: str,
    request: UpdateCartItemRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update cart item quantity."""
    try:
        cart = await order_service.update_cart_item(
            current_user["sub"],
            product_id,
            request.quantity
        )
        
        return CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            items=[
                CartItemResponse(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price
                )
                for item in cart.items
            ],
            total_amount=cart.total_amount,
            currency=cart.currency,
            created_at=cart.created_at.isoformat(),
            updated_at=cart.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/cart/items/{product_id}", response_model=CartResponse)
async def remove_from_cart(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove item from cart."""
    try:
        cart = await order_service.remove_from_cart(current_user["sub"], product_id)
        
        return CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            items=[
                CartItemResponse(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price
                )
                for item in cart.items
            ],
            total_amount=cart.total_amount,
            currency=cart.currency,
            created_at=cart.created_at.isoformat(),
            updated_at=cart.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/cart", response_model=CartResponse)
async def clear_cart(current_user: dict = Depends(get_current_user)):
    """Clear all items from cart."""
    try:
        cart = await order_service.clear_cart(current_user["sub"])
        
        return CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            items=[],
            total_amount=cart.total_amount,
            currency=cart.currency,
            created_at=cart.created_at.isoformat(),
            updated_at=cart.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Order endpoints
@router.post("/", response_model=OrderResponse)
async def create_order(
    request: CreateOrderRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create order from cart."""
    try:
        # Convert address request to Address model
        shipping_address = Address(
            street=request.shipping_address.street,
            city=request.shipping_address.city,
            state=request.shipping_address.state,
            postal_code=request.shipping_address.postal_code or "000000",
            country=request.shipping_address.country
        )
        
        # Create payment method (simplified for API)
        payment_method = PaymentMethod(
            type=PaymentMethodType.CARD,
            details={
                "card_number": "4111111111111111",
                "expiry_month": "12",
                "expiry_year": "2025",
                "cvv": "123",
                "cardholder_name": "Test User"
            }
        )
        
        order = await order_service.create_order(
            current_user["sub"],
            request.cart_id,
            shipping_address,
            payment_method
        )
        
        return OrderResponse(
            id=order.id,
            buyer_id=order.buyer_id,
            seller_id=order.seller_id,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price
                )
                for item in order.items
            ],
            total_amount=order.total_amount,
            currency=order.currency,
            status=order.status.value,
            shipping_address=AddressRequest(
                street=order.shipping_address.street,
                city=order.shipping_address.city,
                state=order.shipping_address.state,
                postal_code=order.shipping_address.postal_code,
                country=order.shipping_address.country
            ),
            payment_info=PaymentInfoResponse(
                payment_method=order.payment_info.payment_method,
                payment_status=order.payment_info.payment_status.value,
                transaction_id=order.payment_info.transaction_id,
                payment_date=order.payment_info.payment_date.isoformat() if order.payment_info.payment_date else None,
                amount=order.payment_info.amount,
                currency=order.payment_info.currency
            ),
            tracking_number=order.tracking_number,
            created_at=order.created_at.isoformat(),
            updated_at=order.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get order by ID."""
    order = await order_service.get_order_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if user has access to this order
    if order.buyer_id != current_user["sub"] and order.seller_id != current_user["sub"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return OrderResponse(
        id=order.id,
        buyer_id=order.buyer_id,
        seller_id=order.seller_id,
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price
            )
            for item in order.items
        ],
        total_amount=order.total_amount,
        currency=order.currency,
        status=order.status.value,
        shipping_address=AddressRequest(
            street=order.shipping_address.street,
            city=order.shipping_address.city,
            state=order.shipping_address.state,
            postal_code=order.shipping_address.postal_code,
            country=order.shipping_address.country
        ),
        payment_info=PaymentInfoResponse(
            payment_method=order.payment_info.payment_method,
            payment_status=order.payment_info.payment_status.value,
            transaction_id=order.payment_info.transaction_id,
            payment_date=order.payment_info.payment_date.isoformat() if order.payment_info.payment_date else None,
            amount=order.payment_info.amount,
            currency=order.payment_info.currency
        ),
        tracking_number=order.tracking_number,
        created_at=order.created_at.isoformat(),
        updated_at=order.updated_at.isoformat()
    )


@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(current_user: dict = Depends(get_current_user)):
    """Get all orders for current user."""
    if current_user["role"] == "buyer":
        orders = await order_service.get_orders_by_buyer(current_user["sub"])
    else:  # seller
        orders = await order_service.get_orders_by_seller(current_user["sub"])
    
    return [
        OrderResponse(
            id=order.id,
            buyer_id=order.buyer_id,
            seller_id=order.seller_id,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price
                )
                for item in order.items
            ],
            total_amount=order.total_amount,
            currency=order.currency,
            status=order.status.value,
            shipping_address=AddressRequest(
                street=order.shipping_address.street,
                city=order.shipping_address.city,
                state=order.shipping_address.state,
                postal_code=order.shipping_address.postal_code,
                country=order.shipping_address.country
            ),
            payment_info=PaymentInfoResponse(
                payment_method=order.payment_info.payment_method,
                payment_status=order.payment_info.payment_status.value,
                transaction_id=order.payment_info.transaction_id,
                payment_date=order.payment_info.payment_date.isoformat() if order.payment_info.payment_date else None,
                amount=order.payment_info.amount,
                currency=order.payment_info.currency
            ),
            tracking_number=order.tracking_number,
            created_at=order.created_at.isoformat(),
            updated_at=order.updated_at.isoformat()
        )
        for order in orders
    ]


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status: OrderStatus,
    current_user: dict = Depends(get_current_user)
):
    """Update order status (sellers only, own orders)."""
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can update order status")
    
    # Check if order exists and belongs to seller
    existing_order = await order_service.get_order_by_id(order_id)
    if not existing_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if existing_order.seller_id != current_user["sub"]:
        raise HTTPException(status_code=403, detail="You can only update your own orders")
    
    try:
        order = await order_service.update_order_status(order_id, status)
        
        return OrderResponse(
            id=order.id,
            buyer_id=order.buyer_id,
            seller_id=order.seller_id,
            items=[
                OrderItemResponse(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price
                )
                for item in order.items
            ],
            total_amount=order.total_amount,
            currency=order.currency,
            status=order.status.value,
            shipping_address=AddressRequest(
                street=order.shipping_address.street,
                city=order.shipping_address.city,
                state=order.shipping_address.state,
                postal_code=order.shipping_address.postal_code,
                country=order.shipping_address.country
            ),
            payment_info=PaymentInfoResponse(
                payment_method=order.payment_info.payment_method,
                payment_status=order.payment_info.payment_status.value,
                transaction_id=order.payment_info.transaction_id,
                payment_date=order.payment_info.payment_date.isoformat() if order.payment_info.payment_date else None,
                amount=order.payment_info.amount,
                currency=order.payment_info.currency
            ),
            tracking_number=order.tracking_number,
            created_at=order.created_at.isoformat(),
            updated_at=order.updated_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))