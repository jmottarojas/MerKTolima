"""Order repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, desc

from ...shared.models import Cart, Order, OrderStatus, CartItem, OrderItem, Address, PaymentInfo
from ...shared.db_models import CartDB, CartItemDB, OrderDB, OrderItemDB


class OrderRepository(ABC):
    """Abstract order repository interface."""
    
    @abstractmethod
    async def create_cart(self, user_id: str) -> Cart:
        """Create a new cart."""
        pass
    
    @abstractmethod
    async def get_cart_by_user(self, user_id: str) -> Optional[Cart]:
        """Get cart by user ID."""
        pass
    
    @abstractmethod
    async def update_cart(self, cart: Cart) -> Cart:
        """Update cart."""
        pass
    
    @abstractmethod
    async def delete_cart(self, cart_id: str) -> None:
        """Delete cart."""
        pass
    
    @abstractmethod
    async def create_order(self, order: Order) -> Order:
        """Create a new order."""
        pass
    
    @abstractmethod
    async def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        pass
    
    @abstractmethod
    async def update_order_status(self, order_id: str, status: OrderStatus) -> Order:
        """Update order status."""
        pass
    
    @abstractmethod
    async def get_orders_by_buyer(self, buyer_id: str) -> List[Order]:
        """Get orders by buyer."""
        pass
    
    @abstractmethod
    async def get_orders_by_seller(self, seller_id: str) -> List[Order]:
        """Get orders by seller."""
        pass
    
    @abstractmethod
    async def generate_tracking_number(self) -> str:
        """Generate unique tracking number."""
        pass


class SQLAlchemyOrderRepository(OrderRepository):
    """SQLAlchemy implementation of order repository."""
    
    def __init__(self, db_session: Session):
        """Initialize with database session."""
        self.db = db_session
    
    def _db_cart_to_pydantic(self, db_cart: CartDB) -> Cart:
        """Convert SQLAlchemy cart model to Pydantic model."""
        items = []
        for db_item in db_cart.items:
            item = CartItem(
                product_id=db_item.product_id,
                quantity=db_item.quantity,
                unit_price=db_item.unit_price,
                total_price=db_item.total_price
            )
            items.append(item)
        
        return Cart(
            id=db_cart.id,
            user_id=db_cart.user_id,
            items=items,
            total_amount=db_cart.total_amount,
            currency=db_cart.currency,
            created_at=db_cart.created_at,
            updated_at=db_cart.updated_at
        )
    
    def _db_order_to_pydantic(self, db_order: OrderDB) -> Order:
        """Convert SQLAlchemy order model to Pydantic model."""
        items = []
        for db_item in db_order.items:
            item = OrderItem(
                product_id=db_item.product_id,
                quantity=db_item.quantity,
                unit_price=db_item.unit_price,
                total_price=db_item.total_price
            )
            items.append(item)
        
        # Parse address and payment info from JSON
        shipping_address = Address(**db_order.shipping_address)
        
        # Handle Decimal conversion in payment_info
        payment_info_data = db_order.payment_info.copy()
        if 'amount' in payment_info_data:
            payment_info_data['amount'] = Decimal(str(payment_info_data['amount']))
        payment_info = PaymentInfo(**payment_info_data)
        
        return Order(
            id=db_order.id,
            buyer_id=db_order.buyer_id,
            seller_id=db_order.seller_id,
            items=items,
            total_amount=db_order.total_amount,
            currency=db_order.currency,
            status=db_order.status,
            shipping_address=shipping_address,
            payment_info=payment_info,
            tracking_number=db_order.tracking_number,
            created_at=db_order.created_at,
            updated_at=db_order.updated_at
        )
    
    async def create_cart(self, user_id: str) -> Cart:
        """Create a new cart."""
        cart_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        db_cart = CartDB(
            id=cart_id,
            user_id=user_id,
            total_amount=Decimal('0.00'),
            currency="USD",
            created_at=now,
            updated_at=now
        )
        
        try:
            self.db.add(db_cart)
            self.db.commit()
            self.db.refresh(db_cart)
            return self._db_cart_to_pydantic(db_cart)
        except Exception:
            self.db.rollback()
            raise
    
    async def get_cart_by_user(self, user_id: str) -> Optional[Cart]:
        """Get cart by user ID."""
        db_cart = self.db.query(CartDB).filter(CartDB.user_id == user_id).first()
        if db_cart:
            return self._db_cart_to_pydantic(db_cart)
        return None
    
    async def update_cart(self, cart: Cart) -> Cart:
        """Update cart."""
        db_cart = self.db.query(CartDB).filter(CartDB.id == cart.id).first()
        if not db_cart:
            raise ValueError(f"Cart {cart.id} not found")
        
        # Update cart fields
        db_cart.total_amount = cart.total_amount
        db_cart.currency = cart.currency
        db_cart.updated_at = datetime.utcnow()
        
        # Delete existing items
        self.db.query(CartItemDB).filter(CartItemDB.cart_id == cart.id).delete()
        
        # Add new items
        for item in cart.items:
            db_item = CartItemDB(
                id=str(uuid.uuid4()),
                cart_id=cart.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(db_item)
        
        try:
            self.db.commit()
            self.db.refresh(db_cart)
            return self._db_cart_to_pydantic(db_cart)
        except Exception:
            self.db.rollback()
            raise
    
    async def delete_cart(self, cart_id: str) -> None:
        """Delete cart."""
        db_cart = self.db.query(CartDB).filter(CartDB.id == cart_id).first()
        if db_cart:
            self.db.delete(db_cart)
            self.db.commit()
    
    async def create_order(self, order: Order) -> Order:
        """Create a new order."""
        # Convert Decimal to string for JSON serialization
        payment_info_dict = order.payment_info.dict()
        if 'amount' in payment_info_dict:
            payment_info_dict['amount'] = str(payment_info_dict['amount'])
        
        db_order = OrderDB(
            id=order.id,
            buyer_id=order.buyer_id,
            seller_id=order.seller_id,
            total_amount=order.total_amount,
            currency=order.currency,
            status=order.status,
            shipping_address=order.shipping_address.dict(),
            payment_info=payment_info_dict,
            tracking_number=order.tracking_number,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        
        try:
            self.db.add(db_order)
            
            # Add order items
            for item in order.items:
                db_item = OrderItemDB(
                    id=str(uuid.uuid4()),
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                    created_at=datetime.utcnow()
                )
                self.db.add(db_item)
            
            self.db.commit()
            self.db.refresh(db_order)
            return self._db_order_to_pydantic(db_order)
        except Exception:
            self.db.rollback()
            raise
    
    async def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        db_order = self.db.query(OrderDB).filter(OrderDB.id == order_id).first()
        if db_order:
            return self._db_order_to_pydantic(db_order)
        return None
    
    async def update_order_status(self, order_id: str, status: OrderStatus) -> Order:
        """Update order status."""
        db_order = self.db.query(OrderDB).filter(OrderDB.id == order_id).first()
        if not db_order:
            raise ValueError(f"Order {order_id} not found")
        
        db_order.status = status
        db_order.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(db_order)
            return self._db_order_to_pydantic(db_order)
        except Exception:
            self.db.rollback()
            raise
    
    async def get_orders_by_buyer(self, buyer_id: str) -> List[Order]:
        """Get orders by buyer."""
        db_orders = self.db.query(OrderDB).filter(OrderDB.buyer_id == buyer_id).order_by(desc(OrderDB.created_at)).all()
        return [self._db_order_to_pydantic(db_order) for db_order in db_orders]
    
    async def get_orders_by_seller(self, seller_id: str) -> List[Order]:
        """Get orders by seller."""
        db_orders = self.db.query(OrderDB).filter(OrderDB.seller_id == seller_id).order_by(desc(OrderDB.created_at)).all()
        return [self._db_order_to_pydantic(db_order) for db_order in db_orders]
    
    async def generate_tracking_number(self) -> str:
        """Generate unique tracking number."""
        return f"TRK{str(uuid.uuid4()).replace('-', '').upper()[:12]}"


class InMemoryOrderRepository(OrderRepository):
    """In-memory implementation of order repository."""
    
    def __init__(self):
        """Initialize repository."""
        self._carts: Dict[str, Cart] = {}
        self._orders: Dict[str, Order] = {}
    
    async def create_cart(self, user_id: str) -> Cart:
        """Create a new cart."""
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
    
    async def get_cart_by_user(self, user_id: str) -> Optional[Cart]:
        """Get cart by user ID."""
        for cart in self._carts.values():
            if cart.user_id == user_id:
                return cart
        return None
    
    async def update_cart(self, cart: Cart) -> Cart:
        """Update cart."""
        cart.updated_at = datetime.utcnow()
        self._carts[cart.id] = cart
        return cart
    
    async def delete_cart(self, cart_id: str) -> None:
        """Delete cart."""
        if cart_id in self._carts:
            del self._carts[cart_id]
    
    async def create_order(self, order: Order) -> Order:
        """Create a new order."""
        self._orders[order.id] = order
        return order
    
    async def get_order_by_id(self, order_id: str) -> Optional[Order]:
        """Get order by ID."""
        return self._orders.get(order_id)
    
    async def update_order_status(self, order_id: str, status: OrderStatus) -> Order:
        """Update order status."""
        order = self._orders.get(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        updated_order = order.copy(update={
            'status': status,
            'updated_at': datetime.utcnow()
        })
        self._orders[order_id] = updated_order
        return updated_order
    
    async def get_orders_by_buyer(self, buyer_id: str) -> List[Order]:
        """Get orders by buyer."""
        return [order for order in self._orders.values() if order.buyer_id == buyer_id]
    
    async def get_orders_by_seller(self, seller_id: str) -> List[Order]:
        """Get orders by seller."""
        return [order for order in self._orders.values() if order.seller_id == seller_id]
    
    async def generate_tracking_number(self) -> str:
        """Generate unique tracking number."""
        return f"TRK{str(uuid.uuid4()).replace('-', '').upper()[:12]}"