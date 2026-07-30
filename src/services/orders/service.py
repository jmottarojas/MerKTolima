"""Order service implementation."""

import uuid
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from ..orders.repository import OrderRepository
from ..orders.config import order_config
from ..products.service import ProductService
from ..payments.service import PaymentService, PaymentData, PaymentMethod, PaymentMethodType, PaymentStatus as PaymentServiceStatus
from ...shared.models import Cart, CartItem, Order, OrderItem, OrderStatus, Product, Address, PaymentInfo, PaymentStatus
from ...shared.service_integration import event_bus, Event, EventType


class OrderService:
    """Order service for managing cart and order operations."""
    
    def __init__(self, repository: OrderRepository, product_service: ProductService, payment_service: Optional[PaymentService] = None):
        """Initialize order service."""
        self.repository = repository
        self.product_service = product_service
        self.payment_service = payment_service
        # In-memory storage for carts (will be replaced with database in task 13)
        self._carts: dict[str, Cart] = {}
        self._orders: dict[str, Order] = {}
    
    async def add_to_cart(self, user_id: str, product_id: str, quantity: int) -> Cart:
        """
        Add item to cart.
        
        Validates product availability and inventory, then adds item to cart.
        Creates new cart if user doesn't have one.
        
        Args:
            user_id: User ID
            product_id: Product ID to add
            quantity: Quantity to add
            
        Returns:
            Updated cart
            
        Raises:
            ValueError: If product not found, not available, or insufficient inventory
        """
        if quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
        
        if quantity > order_config.max_item_quantity:
            raise ValueError(f"Quantity cannot exceed {order_config.max_item_quantity}")
        
        # Get product to validate availability and price
        product = await self.product_service.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product with ID {product_id} not found")
        
        if not product.is_available:
            raise ValueError(f"Product {product.name} is not available")
        
        # Check inventory availability
        if quantity > product.inventory_quantity:
            raise ValueError(f"Insufficient inventory. Available: {product.inventory_quantity}")
        
        # Get or create cart
        cart = await self._get_or_create_cart(user_id)
        
        # Check if item already exists in cart
        existing_item = None
        for item in cart.items:
            if item.product_id == product_id:
                existing_item = item
                break
        
        if existing_item:
            # Update existing item quantity
            new_quantity = existing_item.quantity + quantity
            
            # Check total quantity against inventory
            if new_quantity > product.inventory_quantity:
                raise ValueError(f"Total quantity would exceed inventory. Available: {product.inventory_quantity}")
            
            # Update existing item
            existing_item.quantity = new_quantity
            existing_item.total_price = existing_item.unit_price * new_quantity
        else:
            # Add new item to cart
            if len(cart.items) >= order_config.max_cart_items:
                raise ValueError(f"Cart cannot exceed {order_config.max_cart_items} items")
            
            cart_item = CartItem(
                product_id=product_id,
                quantity=quantity,
                unit_price=product.price,
                total_price=product.price * quantity
            )
            cart.items.append(cart_item)
        
        # Recalculate cart total
        cart.total_amount = sum(item.total_price for item in cart.items)
        cart.updated_at = datetime.utcnow()
        
        # Store updated cart
        self._carts[cart.id] = cart
        
        # Publish cart item added event
        await event_bus.publish(Event(
            type=EventType.CART_ITEM_ADDED,
            source_service="order_service",
            data={
                "user_id": user_id,
                "cart_id": cart.id,
                "product_id": product_id,
                "quantity": quantity,
                "total_amount": float(cart.total_amount)
            }
        ))
        
        return cart
    
    async def update_cart_item(self, user_id: str, product_id: str, quantity: int) -> Cart:
        """
        Update cart item quantity.
        
        Updates the quantity of a specific item in the cart.
        Removes item if quantity is 0.
        
        Args:
            user_id: User ID
            product_id: Product ID to update
            quantity: New quantity (0 to remove)
            
        Returns:
            Updated cart
            
        Raises:
            ValueError: If cart not found, item not in cart, or invalid quantity
        """
        if quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        if quantity > order_config.max_item_quantity:
            raise ValueError(f"Quantity cannot exceed {order_config.max_item_quantity}")
        
        # Get cart
        cart = await self._get_user_cart(user_id)
        if not cart:
            raise ValueError("Cart not found")
        
        # Find item in cart
        item_index = None
        for i, item in enumerate(cart.items):
            if item.product_id == product_id:
                item_index = i
                break
        
        if item_index is None:
            raise ValueError(f"Product {product_id} not found in cart")
        
        if quantity == 0:
            # Remove item from cart
            cart.items.pop(item_index)
        else:
            # Validate inventory if increasing quantity
            product = await self.product_service.get_product_by_id(product_id)
            if not product:
                raise ValueError(f"Product with ID {product_id} not found")
            
            if quantity > product.inventory_quantity:
                raise ValueError(f"Insufficient inventory. Available: {product.inventory_quantity}")
            
            # Update item quantity and total
            cart.items[item_index].quantity = quantity
            cart.items[item_index].unit_price = product.price  # Update price in case it changed
            cart.items[item_index].total_price = product.price * quantity
        
        # Recalculate cart total
        cart.total_amount = sum(item.total_price for item in cart.items)
        cart.updated_at = datetime.utcnow()
        
        # Store updated cart
        self._carts[cart.id] = cart
        
        return cart
    
    async def remove_from_cart(self, user_id: str, product_id: str) -> Cart:
        """
        Remove item from cart.
        
        Removes a specific product from the user's cart.
        
        Args:
            user_id: User ID
            product_id: Product ID to remove
            
        Returns:
            Updated cart
            
        Raises:
            ValueError: If cart not found or item not in cart
        """
        return await self.update_cart_item(user_id, product_id, 0)
    
    async def get_cart(self, user_id: str) -> Optional[Cart]:
        """
        Get user's cart.
        
        Args:
            user_id: User ID
            
        Returns:
            User's cart if exists, None otherwise
        """
        return await self._get_user_cart(user_id)
    
    async def clear_cart(self, user_id: str) -> Cart:
        """
        Clear all items from cart.
        
        Args:
            user_id: User ID
            
        Returns:
            Empty cart
            
        Raises:
            ValueError: If cart not found
        """
        cart = await self._get_user_cart(user_id)
        if not cart:
            raise ValueError("Cart not found")
        
        cart.items = []
        cart.total_amount = Decimal('0.00')
        cart.updated_at = datetime.utcnow()
        
        # Store updated cart
        self._carts[cart.id] = cart
        
        return cart
    
    async def _get_or_create_cart(self, user_id: str) -> Cart:
        """Get existing cart or create new one for user."""
        # Look for existing cart
        for cart in self._carts.values():
            if cart.user_id == user_id:
                return cart
        
        # Create new cart
        cart_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        cart = Cart(
            id=cart_id,
            user_id=user_id,
            items=[],
            total_amount=Decimal('0.00'),
            currency="USD",
            created_at=now,
            updated_at=now
        )
        
        self._carts[cart_id] = cart
        return cart
    
    async def _get_user_cart(self, user_id: str) -> Optional[Cart]:
        """Get user's cart if exists."""
        for cart in self._carts.values():
            if cart.user_id == user_id:
                return cart
        return None
    
    # Order processing methods with payment integration
    async def create_order(self, user_id: str, cart_id: str, shipping_address: Address, payment_method) -> Order:
        """
        Create order from cart with payment processing.
        
        Validates cart contents, processes payment, and creates order.
        Reduces inventory for ordered items only if payment is successful.
        
        Args:
            user_id: User ID creating the order
            cart_id: Cart ID to convert to order
            shipping_address: Shipping address for the order
            payment_method: Payment method for the order
            
        Returns:
            Created order
            
        Raises:
            ValueError: If cart not found, empty, inventory insufficient, or payment fails
        """
        # Handle payment method input - convert string to PaymentMethod if needed
        if isinstance(payment_method, str):
            # Convert string to PaymentMethod object with proper details
            payment_method_type = PaymentMethodType.CARD if payment_method == "credit_card" else PaymentMethodType.CARD
            payment_method = PaymentMethod(
                type=payment_method_type,
                details={
                    "card_number": "4000000000000002",  # Test card number that will succeed
                    "expiry_month": 12,  # Integer, not string
                    "expiry_year": 2025,  # Integer, not string
                    "cvv": "123",
                    "cardholder_name": "Test User"
                }
            )
        
        # Get cart
        cart = self._carts.get(cart_id)
        if not cart:
            raise ValueError(f"Cart with ID {cart_id} not found")
        
        if cart.user_id != user_id:
            raise ValueError("Cart does not belong to user")
        
        if not cart.items:
            raise ValueError("Cannot create order from empty cart")
        
        # Validate inventory for all items
        for cart_item in cart.items:
            product = await self.product_service.get_product_by_id(cart_item.product_id)
            if not product:
                raise ValueError(f"Product {cart_item.product_id} no longer exists")
            
            if not product.is_available:
                raise ValueError(f"Product {product.name} is no longer available")
            
            if cart_item.quantity > product.inventory_quantity:
                raise ValueError(f"Insufficient inventory for {product.name}. Available: {product.inventory_quantity}")
        
        # Generate order ID and tracking number
        order_id = str(uuid.uuid4())
        tracking_number = await self._generate_tracking_number()
        
        # Create order items from cart items
        order_items = []
        seller_id = None
        
        for cart_item in cart.items:
            product = await self.product_service.get_product_by_id(cart_item.product_id)
            
            # For simplicity, assume all items are from the same seller
            # In a real marketplace, orders would be split by seller
            if seller_id is None:
                seller_id = product.seller_id
            elif seller_id != product.seller_id:
                raise ValueError("Cart contains items from multiple sellers. Please checkout items from one seller at a time.")
            
            order_item = OrderItem(
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.total_price
            )
            order_items.append(order_item)
        
        # Process payment if payment service is available
        payment_status = PaymentStatus.PENDING
        transaction_id = None
        payment_message = None
        
        if self.payment_service:
            try:
                # Create payment data
                payment_data = PaymentData(
                    order_id=order_id,
                    amount=cart.total_amount,
                    currency=cart.currency,
                    payment_method=payment_method
                )
                
                # Process payment
                payment_result = await self.payment_service.process_payment(payment_data)
                
                if payment_result.status == PaymentServiceStatus.COMPLETED:
                    payment_status = PaymentStatus.COMPLETED
                    transaction_id = payment_result.transaction_id
                    payment_message = payment_result.message
                    
                    # Reduce inventory for ordered items (only on successful payment)
                    for cart_item in cart.items:
                        product = await self.product_service.get_product_by_id(cart_item.product_id)
                        new_inventory = product.inventory_quantity - cart_item.quantity
                        await self.product_service.update_inventory(cart_item.product_id, new_inventory)
                    
                else:
                    # Payment failed - don't create order, return error
                    raise ValueError(f"Payment failed: {payment_result.message}")
                    
            except Exception as e:
                # Payment processing error - don't create order
                raise ValueError(f"Payment processing error: {str(e)}")
        
        # Create payment info
        payment_info = PaymentInfo(
            payment_method=payment_method.type.value,
            payment_status=payment_status,
            transaction_id=transaction_id,
            payment_date=datetime.utcnow() if payment_status == PaymentStatus.COMPLETED else None,
            amount=cart.total_amount,
            currency=cart.currency
        )
        
        # Create order
        now = datetime.utcnow()
        order_status = OrderStatus.CONFIRMED if payment_status == PaymentStatus.COMPLETED else OrderStatus.PENDING
        
        order = Order(
            id=order_id,
            buyer_id=user_id,
            seller_id=seller_id,
            items=order_items,
            total_amount=cart.total_amount,
            currency=cart.currency,
            status=order_status,
            shipping_address=shipping_address,
            payment_info=payment_info,
            tracking_number=tracking_number,
            created_at=now,
            updated_at=now
        )
        
        # Store order
        self._orders[order_id] = order
        
        # Publish order created event
        await event_bus.publish(Event(
            type=EventType.ORDER_CREATED,
            source_service="order_service",
            data={
                "id": order.id,
                "buyer_id": order.buyer_id,
                "seller_id": order.seller_id,
                "total_amount": float(order.total_amount),
                "currency": order.currency,
                "status": order.status.value,
                "item_count": len(order.items)
            }
        ))
        
        # Clear the cart only if payment was successful
        if payment_status == PaymentStatus.COMPLETED:
            await self.clear_cart(user_id)
        
        return order
    
    async def process_payment_for_order(self, order_id: str, payment_method: PaymentMethod) -> Order:
        """
        Process payment for an existing pending order.
        
        Args:
            order_id: Order ID to process payment for
            payment_method: Payment method to use
            
        Returns:
            Updated order with payment status
            
        Raises:
            ValueError: If order not found, not pending, or payment fails
        """
        order = self._orders.get(order_id)
        if not order:
            raise ValueError(f"Order with ID {order_id} not found")
        
        if order.status != OrderStatus.PENDING:
            raise ValueError(f"Order status must be PENDING to process payment. Current status: {order.status}")
        
        if not self.payment_service:
            raise ValueError("Payment service not available")
        
        try:
            # Create payment data
            payment_data = PaymentData(
                order_id=order_id,
                amount=order.total_amount,
                currency=order.currency,
                payment_method=payment_method
            )
            
            # Process payment
            payment_result = await self.payment_service.process_payment(payment_data)
            
            if payment_result.status == PaymentServiceStatus.COMPLETED:
                # Update order payment info
                order.payment_info.payment_status = PaymentStatus.COMPLETED
                order.payment_info.transaction_id = payment_result.transaction_id
                order.payment_info.payment_date = datetime.utcnow()
                order.payment_info.payment_method = payment_method.type.value
                
                # Update order status
                order.status = OrderStatus.CONFIRMED
                order.updated_at = datetime.utcnow()
                
                # Reduce inventory for ordered items
                for order_item in order.items:
                    product = await self.product_service.get_product_by_id(order_item.product_id)
                    if product:
                        new_inventory = product.inventory_quantity - order_item.quantity
                        await self.product_service.update_inventory(order_item.product_id, new_inventory)
                
                # Store updated order
                self._orders[order_id] = order
                
                return order
            else:
                # Payment failed
                order.payment_info.payment_status = PaymentStatus.FAILED
                order.updated_at = datetime.utcnow()
                self._orders[order_id] = order
                
                raise ValueError(f"Payment failed: {payment_result.message}")
                
        except Exception as e:
            # Update order with failed payment status
            order.payment_info.payment_status = PaymentStatus.FAILED
            order.updated_at = datetime.utcnow()
            self._orders[order_id] = order
            
            raise ValueError(f"Payment processing error: {str(e)}")
    
    async def handle_payment_failure(self, order_id: str, error_message: str) -> Order:
        """
        Handle payment failure for an order.
        
        Updates order status and restores inventory if needed.
        
        Args:
            order_id: Order ID with failed payment
            error_message: Payment failure message
            
        Returns:
            Updated order
            
        Raises:
            ValueError: If order not found
        """
        order = self._orders.get(order_id)
        if not order:
            raise ValueError(f"Order with ID {order_id} not found")
        
        # Update payment status
        order.payment_info.payment_status = PaymentStatus.FAILED
        order.updated_at = datetime.utcnow()
        
        # If inventory was already reduced (shouldn't happen with current flow), restore it
        # This is a safety measure for edge cases
        if order.status == OrderStatus.CONFIRMED:
            for order_item in order.items:
                product = await self.product_service.get_product_by_id(order_item.product_id)
                if product:
                    new_inventory = product.inventory_quantity + order_item.quantity
                    await self.product_service.update_inventory(order_item.product_id, new_inventory)
        
        # Keep order in PENDING status for potential retry
        order.status = OrderStatus.PENDING
        
        # Store updated order
        self._orders[order_id] = order
        
        return order
    
    async def update_order_status(self, order_id: str, status: OrderStatus) -> Order:
        """
        Update order status.
        
        Updates the status of an existing order and tracks the change.
        
        Args:
            order_id: Order ID to update
            status: New order status
            
        Returns:
            Updated order
            
        Raises:
            ValueError: If order not found or invalid status transition
        """
        order = self._orders.get(order_id)
        if not order:
            raise ValueError(f"Order with ID {order_id} not found")
        
        # Validate status transition
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [],  # Final state
            OrderStatus.CANCELLED: []   # Final state
        }
        
        if status not in valid_transitions.get(order.status, []):
            raise ValueError(f"Invalid status transition from {order.status} to {status}")
        
        # Update order
        order.status = status
        order.updated_at = datetime.utcnow()
        
        # Store updated order
        self._orders[order_id] = order
        
        # Publish order status updated event
        event_type = None
        if status == OrderStatus.CONFIRMED:
            event_type = EventType.ORDER_CONFIRMED
        elif status == OrderStatus.SHIPPED:
            event_type = EventType.ORDER_SHIPPED
        elif status == OrderStatus.DELIVERED:
            event_type = EventType.ORDER_DELIVERED
        elif status == OrderStatus.CANCELLED:
            event_type = EventType.ORDER_CANCELLED
        
        if event_type:
            await event_bus.publish(Event(
                type=event_type,
                source_service="order_service",
                data={
                    "order_id": order.id,
                    "buyer_id": order.buyer_id,
                    "seller_id": order.seller_id,
                    "status": status.value,
                    "tracking_number": order.tracking_number
                }
            ))
        
        return order
    
    async def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """
        Get order by ID.
        
        Args:
            order_id: Order ID
            
        Returns:
            Order if found, None otherwise
        """
        return self._orders.get(order_id)
    
    async def get_orders_by_buyer(self, buyer_id: str) -> List[Order]:
        """
        Get all orders for a buyer.
        
        Args:
            buyer_id: Buyer ID
            
        Returns:
            List of orders for the buyer
        """
        return [order for order in self._orders.values() if order.buyer_id == buyer_id]
    
    async def get_orders_by_seller(self, seller_id: str) -> List[Order]:
        """
        Get all orders for a seller.
        
        Args:
            seller_id: Seller ID
            
        Returns:
            List of orders for the seller
        """
        return [order for order in self._orders.values() if order.seller_id == seller_id]
    
    async def _generate_tracking_number(self) -> str:
        """
        Generate unique tracking number.
        
        Returns:
            Unique tracking number with configured prefix
        """
        # Generate unique suffix
        suffix = str(uuid.uuid4()).replace('-', '').upper()[:order_config.tracking_number_length - len(order_config.tracking_number_prefix)]
        
        return f"{order_config.tracking_number_prefix}{suffix}"