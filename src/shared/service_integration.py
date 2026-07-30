"""Service integration layer for inter-service communication."""

import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
import uuid
import logging

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types for inter-service communication."""
    # User events
    USER_REGISTERED = "user.registered"
    USER_PROFILE_UPDATED = "user.profile_updated"
    
    # Product events
    PRODUCT_CREATED = "product.created"
    PRODUCT_UPDATED = "product.updated"
    PRODUCT_INVENTORY_LOW = "product.inventory_low"
    PRODUCT_OUT_OF_STOCK = "product.out_of_stock"
    
    # Order events
    ORDER_CREATED = "order.created"
    ORDER_CONFIRMED = "order.confirmed"
    ORDER_SHIPPED = "order.shipped"
    ORDER_DELIVERED = "order.delivered"
    ORDER_CANCELLED = "order.cancelled"
    
    # Payment events
    PAYMENT_INITIATED = "payment.initiated"
    PAYMENT_COMPLETED = "payment.completed"
    PAYMENT_FAILED = "payment.failed"
    PAYMENT_REFUNDED = "payment.refunded"
    
    # Cart events
    CART_ITEM_ADDED = "cart.item_added"
    CART_UPDATED = "cart.updated"


class Event(BaseModel):
    """Event model for inter-service communication."""
    id: str = None
    type: EventType
    source_service: str
    timestamp: datetime = None
    data: Dict[str, Any]
    correlation_id: Optional[str] = None
    
    def __init__(self, **data):
        if 'id' not in data or data['id'] is None:
            data['id'] = str(uuid.uuid4())
        if 'timestamp' not in data or data['timestamp'] is None:
            data['timestamp'] = datetime.utcnow()
        super().__init__(**data)


class EventBus:
    """Simple in-memory event bus for service communication."""
    
    def __init__(self):
        """Initialize event bus."""
        self._handlers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []
    
    def subscribe(self, event_type: EventType, handler: Callable[[Event], None]):
        """Subscribe to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Handler subscribed to {event_type}")
    
    async def publish(self, event: Event):
        """Publish an event to all subscribers."""
        self._event_history.append(event)
        logger.info(f"Publishing event: {event.type} from {event.source_service}")
        
        if event.type in self._handlers:
            for handler in self._handlers[event.type]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(event)
                    else:
                        handler(event)
                except Exception as e:
                    logger.error(f"Error handling event {event.type}: {e}")
    
    def get_event_history(self, event_type: Optional[EventType] = None) -> List[Event]:
        """Get event history, optionally filtered by type."""
        if event_type:
            return [e for e in self._event_history if e.type == event_type]
        return self._event_history.copy()


# Global event bus instance
event_bus = EventBus()


class ServiceRegistry:
    """Registry for managing service instances and dependencies."""
    
    def __init__(self):
        """Initialize service registry."""
        self._services: Dict[str, Any] = {}
        self._dependencies: Dict[str, List[str]] = {}
    
    def register_service(self, name: str, service_instance: Any, dependencies: Optional[List[str]] = None):
        """Register a service instance."""
        self._services[name] = service_instance
        self._dependencies[name] = dependencies or []
        logger.info(f"Service registered: {name}")
    
    def get_service(self, name: str) -> Any:
        """Get a service instance."""
        if name not in self._services:
            raise ValueError(f"Service not found: {name}")
        return self._services[name]
    
    def get_dependencies(self, service_name: str) -> List[str]:
        """Get service dependencies."""
        return self._dependencies.get(service_name, [])
    
    def list_services(self) -> List[str]:
        """List all registered services."""
        return list(self._services.keys())


# Global service registry
service_registry = ServiceRegistry()


class BusinessFlowOrchestrator:
    """Orchestrates complex business flows across multiple services."""
    
    def __init__(self, event_bus: EventBus, service_registry: ServiceRegistry):
        """Initialize orchestrator."""
        self.event_bus = event_bus
        self.service_registry = service_registry
        self._setup_event_handlers()
    
    def _setup_event_handlers(self):
        """Setup event handlers for business flow orchestration."""
        # Order flow handlers
        self.event_bus.subscribe(EventType.ORDER_CREATED, self._handle_order_created)
        self.event_bus.subscribe(EventType.PAYMENT_COMPLETED, self._handle_payment_completed)
        self.event_bus.subscribe(EventType.PAYMENT_FAILED, self._handle_payment_failed)
        
        # Inventory management handlers
        self.event_bus.subscribe(EventType.ORDER_CONFIRMED, self._handle_order_confirmed)
        self.event_bus.subscribe(EventType.PRODUCT_INVENTORY_LOW, self._handle_low_inventory)
        
        # Notification handlers
        self.event_bus.subscribe(EventType.USER_REGISTERED, self._handle_user_registered)
        self.event_bus.subscribe(EventType.ORDER_SHIPPED, self._handle_order_shipped)
    
    async def _handle_order_created(self, event: Event):
        """Handle order creation - send notifications."""
        try:
            order_data = event.data
            notification_service = self.service_registry.get_service("notification_service")
            
            # Notify buyer
            await self._send_notification(
                notification_service,
                user_id=order_data["buyer_id"],
                title="Order Confirmed",
                message=f"Your order #{order_data['id']} has been created and is being processed.",
                notification_type="email",
                metadata={"order_id": order_data["id"]}
            )
            
            # Notify seller
            await self._send_notification(
                notification_service,
                user_id=order_data["seller_id"],
                title="New Order Received",
                message=f"You have received a new order #{order_data['id']}.",
                notification_type="email",
                metadata={"order_id": order_data["id"]}
            )
            
        except Exception as e:
            logger.error(f"Error handling order created event: {e}")
    
    async def _handle_payment_completed(self, event: Event):
        """Handle successful payment - update order status."""
        try:
            payment_data = event.data
            order_service = self.service_registry.get_service("order_service")
            
            # Update order status to confirmed
            await order_service.update_order_status(
                payment_data["order_id"], 
                "confirmed"
            )
            
            # Publish order confirmed event
            await self.event_bus.publish(Event(
                type=EventType.ORDER_CONFIRMED,
                source_service="orchestrator",
                data={
                    "order_id": payment_data["order_id"],
                    "payment_id": payment_data["payment_id"]
                },
                correlation_id=event.correlation_id
            ))
            
        except Exception as e:
            logger.error(f"Error handling payment completed event: {e}")
    
    async def _handle_payment_failed(self, event: Event):
        """Handle failed payment - cancel order."""
        try:
            payment_data = event.data
            order_service = self.service_registry.get_service("order_service")
            notification_service = self.service_registry.get_service("notification_service")
            
            # Cancel the order
            await order_service.update_order_status(
                payment_data["order_id"], 
                "cancelled"
            )
            
            # Notify buyer about payment failure
            order = await order_service.get_order_by_id(payment_data["order_id"])
            if order:
                await self._send_notification(
                    notification_service,
                    user_id=order.buyer_id,
                    title="Payment Failed",
                    message=f"Payment for order #{order.id} failed. The order has been cancelled.",
                    notification_type="email",
                    metadata={"order_id": order.id}
                )
            
        except Exception as e:
            logger.error(f"Error handling payment failed event: {e}")
    
    async def _handle_order_confirmed(self, event: Event):
        """Handle order confirmation - update inventory."""
        try:
            order_data = event.data
            order_service = self.service_registry.get_service("order_service")
            product_service = self.service_registry.get_service("product_service")
            
            # Get order details
            order = await order_service.get_order_by_id(order_data["order_id"])
            if not order:
                return
            
            # Update inventory for each item
            for item in order.items:
                await product_service.update_inventory(
                    item.product_id, 
                    -item.quantity  # Reduce inventory
                )
                
                # Check if inventory is low
                product = await product_service.get_product_by_id(item.product_id)
                if product and product.inventory.quantity <= product.inventory.low_stock_threshold:
                    await self.event_bus.publish(Event(
                        type=EventType.PRODUCT_INVENTORY_LOW,
                        source_service="orchestrator",
                        data={
                            "product_id": product.id,
                            "current_quantity": product.inventory.quantity,
                            "threshold": product.inventory.low_stock_threshold
                        }
                    ))
            
        except Exception as e:
            logger.error(f"Error handling order confirmed event: {e}")
    
    async def _handle_low_inventory(self, event: Event):
        """Handle low inventory - notify seller."""
        try:
            inventory_data = event.data
            product_service = self.service_registry.get_service("product_service")
            notification_service = self.service_registry.get_service("notification_service")
            
            # Get product details
            product = await product_service.get_product_by_id(inventory_data["product_id"])
            if not product:
                return
            
            # Notify seller about low inventory
            await self._send_notification(
                notification_service,
                user_id=product.seller_id,
                title="Low Inventory Alert",
                message=f"Product '{product.name}' is running low on inventory. Current stock: {inventory_data['current_quantity']}",
                notification_type="email",
                metadata={"product_id": product.id}
            )
            
        except Exception as e:
            logger.error(f"Error handling low inventory event: {e}")
    
    async def _handle_user_registered(self, event: Event):
        """Handle user registration - send welcome notification."""
        try:
            user_data = event.data
            notification_service = self.service_registry.get_service("notification_service")
            
            await self._send_notification(
                notification_service,
                user_id=user_data["user_id"],
                title="Welcome to Marketplace Platform",
                message=f"Welcome {user_data['first_name']}! Your account has been created successfully.",
                notification_type="email",
                metadata={"user_id": user_data["user_id"]}
            )
            
        except Exception as e:
            logger.error(f"Error handling user registered event: {e}")
    
    async def _handle_order_shipped(self, event: Event):
        """Handle order shipment - notify buyer."""
        try:
            order_data = event.data
            notification_service = self.service_registry.get_service("notification_service")
            
            await self._send_notification(
                notification_service,
                user_id=order_data["buyer_id"],
                title="Order Shipped",
                message=f"Your order #{order_data['order_id']} has been shipped. Tracking number: {order_data.get('tracking_number', 'N/A')}",
                notification_type="email",
                metadata={"order_id": order_data["order_id"]}
            )
            
        except Exception as e:
            logger.error(f"Error handling order shipped event: {e}")
    
    async def _send_notification(self, notification_service, user_id: str, title: str, 
                               message: str, notification_type: str, metadata: Dict[str, Any]):
        """Helper method to send notifications."""
        try:
            from ..services.notifications.service import NotificationData, NotificationType, NotificationChannel
            
            # Map notification type
            notif_type = NotificationType.EMAIL if notification_type == "email" else NotificationType.IN_APP
            
            notification_data = NotificationData(
                user_id=user_id,
                type=notif_type,
                channel=NotificationChannel.ORDER_UPDATES,
                subject=title,
                content=message,
                metadata=metadata
            )
            
            await notification_service.send_notification(notification_data)
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")


# Global orchestrator instance
orchestrator = BusinessFlowOrchestrator(event_bus, service_registry)