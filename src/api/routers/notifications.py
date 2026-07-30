"""Notification endpoints."""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from ...services.notifications.service import NotificationService, NotificationData, NotificationPreferences, NotificationType, NotificationChannel
from ...services.notifications.repository import InMemoryNotificationRepository
from ...shared.models import BaseResponse
from ..dependencies import get_current_user

router = APIRouter(tags=["notifications"])

# Initialize notification service
notification_repository = InMemoryNotificationRepository()
notification_service = NotificationService(notification_repository)


class NotificationRequest(BaseModel):
    """Notification request model."""
    type: str  # "email", "in_app", "sms"
    channel: str  # "order_updates", "price_alerts", "inventory_alerts", "marketing"
    subject: str
    content: str
    metadata: Optional[Dict[str, Any]] = None


class NotificationPreferencesRequest(BaseModel):
    """Notification preferences request model."""
    email_enabled: bool = True
    in_app_enabled: bool = True
    sms_enabled: bool = False
    channels: Dict[str, bool]


class NotificationResponse(BaseModel):
    """Notification response model."""
    id: str
    user_id: str
    type: str
    channel: str
    subject: str
    content: str
    read: bool
    sent_at: str
    read_at: Optional[str] = None


class NotificationPreferencesResponse(BaseModel):
    """Notification preferences response model."""
    email_enabled: bool
    in_app_enabled: bool
    sms_enabled: bool
    channels: Dict[str, bool]


@router.post("/send", response_model=BaseResponse)
async def send_notification(
    request: NotificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Send a notification (admin/system use)."""
    try:
        # Convert string types to enums
        notification_type = NotificationType.IN_APP
        if request.type == "email":
            notification_type = NotificationType.EMAIL
        elif request.type == "sms":
            notification_type = NotificationType.SMS
        
        notification_channel = NotificationChannel.ORDER_UPDATES
        if request.channel == "price_alerts":
            notification_channel = NotificationChannel.PRICE_ALERTS
        elif request.channel == "inventory_alerts":
            notification_channel = NotificationChannel.INVENTORY_ALERTS
        elif request.channel == "marketing":
            notification_channel = NotificationChannel.MARKETING
        
        # Create notification data
        notification_data = NotificationData(
            user_id=current_user["sub"],
            type=notification_type,
            channel=notification_channel,
            subject=request.subject,
            content=request.content,
            metadata=request.metadata
        )
        
        # Send notification
        await notification_service.send_notification(notification_data)
        
        return BaseResponse(
            success=True,
            message="Notification sent successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100, description="Number of notifications to retrieve")
):
    """Get notification history for current user."""
    try:
        notifications = await notification_service.get_notification_history(
            current_user["sub"],
            limit
        )
        
        return [
            NotificationResponse(
                id=notification.id,
                user_id=notification.user_id,
                type=notification.type.value,
                channel=notification.channel.value,
                subject=notification.subject,
                content=notification.content,
                read=notification.read,
                sent_at=notification.sent_at.isoformat(),
                read_at=notification.read_at.isoformat() if notification.read_at else None
            )
            for notification in notifications
        ]
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{notification_id}/read", response_model=BaseResponse)
async def mark_notification_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark a notification as read."""
    try:
        await notification_service.mark_notification_as_read(notification_id)
        
        return BaseResponse(
            success=True,
            message="Notification marked as read"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(current_user: dict = Depends(get_current_user)):
    """Get user's notification preferences."""
    try:
        preferences = await notification_service.get_user_preferences(current_user["sub"])
        
        # Convert enum keys to strings for API response
        channels_dict = {}
        for channel, enabled in preferences.channels.items():
            channels_dict[channel.value] = enabled
        
        return NotificationPreferencesResponse(
            email_enabled=preferences.email_enabled,
            in_app_enabled=preferences.in_app_enabled,
            sms_enabled=preferences.sms_enabled,
            channels=channels_dict
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/preferences", response_model=BaseResponse)
async def update_notification_preferences(
    request: NotificationPreferencesRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update user's notification preferences."""
    try:
        # Convert string keys back to enums
        channels_dict = {}
        for channel_str, enabled in request.channels.items():
            if channel_str == "order_updates":
                channels_dict[NotificationChannel.ORDER_UPDATES] = enabled
            elif channel_str == "price_alerts":
                channels_dict[NotificationChannel.PRICE_ALERTS] = enabled
            elif channel_str == "inventory_alerts":
                channels_dict[NotificationChannel.INVENTORY_ALERTS] = enabled
            elif channel_str == "marketing":
                channels_dict[NotificationChannel.MARKETING] = enabled
        
        preferences = NotificationPreferences(
            email_enabled=request.email_enabled,
            in_app_enabled=request.in_app_enabled,
            sms_enabled=request.sms_enabled,
            channels=channels_dict
        )
        
        await notification_service.update_user_preferences(current_user["sub"], preferences)
        
        return BaseResponse(
            success=True,
            message="Notification preferences updated successfully"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Automatic notification endpoints (for system/admin use)
@router.post("/triggers/new-order", response_model=BaseResponse)
async def trigger_new_order_notification(
    order_id: str,
    seller_id: str,
    seller_email: str,
    order_details: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Trigger new order notification to seller."""
    try:
        await notification_service.notify_new_order_to_seller(
            order_id, seller_id, seller_email, order_details
        )
        
        return BaseResponse(
            success=True,
            message="New order notification sent"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/triggers/order-status-change", response_model=BaseResponse)
async def trigger_order_status_change_notification(
    order_id: str,
    buyer_id: str,
    buyer_email: str,
    old_status: str,
    new_status: str,
    tracking_number: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Trigger order status change notification to buyer."""
    try:
        await notification_service.notify_order_status_change_to_buyer(
            order_id, buyer_id, buyer_email, old_status, new_status, tracking_number
        )
        
        return BaseResponse(
            success=True,
            message="Order status change notification sent"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/triggers/low-inventory", response_model=BaseResponse)
async def trigger_low_inventory_notification(
    product_id: str,
    seller_id: str,
    seller_email: str,
    product_name: str,
    current_quantity: int,
    threshold: int,
    current_user: dict = Depends(get_current_user)
):
    """Trigger low inventory notification to seller."""
    try:
        await notification_service.notify_low_inventory_to_seller(
            product_id, seller_id, seller_email, product_name, current_quantity, threshold
        )
        
        return BaseResponse(
            success=True,
            message="Low inventory notification sent"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/triggers/price-change", response_model=BaseResponse)
async def trigger_price_change_notification(
    product_id: str,
    product_name: str,
    old_price: float,
    new_price: float,
    currency: str,
    user_wishlist: List[Dict[str, str]],
    current_user: dict = Depends(get_current_user)
):
    """Trigger price change notification to wishlist users."""
    try:
        await notification_service.notify_price_change_to_wishlist_users(
            product_id, product_name, old_price, new_price, currency, user_wishlist
        )
        
        return BaseResponse(
            success=True,
            message="Price change notifications sent"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))