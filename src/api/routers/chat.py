"""Chat endpoints for buyer-seller communication."""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from ...services.chat.service import ChatService
from ...shared.models_chat import ChatMessage, ProductChat, MessageStatus
from ..dependencies import get_current_user, get_product_service, get_chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


class SendMessageRequest(BaseModel):
    """Send message request model."""
    product_id: str
    receiver_id: str
    message: str


class MessageResponse(BaseModel):
    """Message response model."""
    id: str
    product_id: str
    sender_id: str
    receiver_id: str
    message: str
    is_filtered: bool
    filter_reason: Optional[str]
    status: str
    created_at: str
    
    @classmethod
    def from_message(cls, message: ChatMessage) -> 'MessageResponse':
        return cls(
            id=message.id,
            product_id=message.product_id,
            sender_id=message.sender_id,
            receiver_id=message.receiver_id,
            message=message.message,
            is_filtered=message.is_filtered,
            filter_reason=message.filter_reason,
            status=message.status.value,
            created_at=message.created_at.isoformat()
        )


class ChatResponse(BaseModel):
    """Chat response model."""
    id: str
    product_id: str
    buyer_id: str
    seller_id: str
    last_message_at: str
    message_count: int
    is_active: bool


class SendMessageResponse(BaseModel):
    """Send message response model."""
    message: MessageResponse
    is_blocked: bool
    warning: Optional[str] = None


@router.post("/messages", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a message in a product chat."""
    try:
        message, is_blocked = await chat_service.send_message(
            product_id=request.product_id,
            sender_id=current_user["sub"],
            receiver_id=request.receiver_id,
            message=request.message
        )
        
        warning = None
        if is_blocked:
            warning = "Tu mensaje contiene información que no está permitida antes de concretar la compra. Se ha filtrado automáticamente."
        elif message.filter_reason:
            warning = "Tu mensaje ha sido revisado por nuestros filtros de seguridad."
        
        return SendMessageResponse(
            message=MessageResponse.from_message(message),
            is_blocked=is_blocked,
            warning=warning
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending message: {str(e)}")


@router.get("/products/{product_id}/messages", response_model=List[MessageResponse])
async def get_product_messages(
    product_id: str,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get all messages for a product chat."""
    try:
        messages = await chat_service.get_chat_messages(product_id, current_user["sub"])
        
        return [MessageResponse.from_message(msg) for msg in messages]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting messages: {str(e)}")


@router.get("/my-chats", response_model=List[ChatResponse])
async def get_my_chats(
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get all chats for the current user."""
    try:
        chats = await chat_service.get_user_chats(current_user["sub"])
        
        return [
            ChatResponse(
                id=chat.id,
                product_id=chat.product_id,
                buyer_id=chat.buyer_id,
                seller_id=chat.seller_id,
                last_message_at=chat.last_message_at.isoformat(),
                message_count=len(chat.messages),
                is_active=chat.is_active
            )
            for chat in chats
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chats: {str(e)}")


@router.post("/products/{product_id}/mark-read")
async def mark_messages_read(
    product_id: str,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Mark all messages in a product chat as read."""
    try:
        marked_count = await chat_service.mark_messages_as_read(product_id, current_user["sub"])
        
        return {
            "success": True,
            "marked_count": marked_count,
            "message": f"Marked {marked_count} messages as read"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking messages as read: {str(e)}")


@router.get("/products/{product_id}/stats")
async def get_chat_stats(
    product_id: str,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get chat statistics for a product (sellers only)."""
    # Note: In a real implementation, you'd verify the user is the seller of the product
    try:
        stats = await chat_service.get_chat_stats(product_id)
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chat stats: {str(e)}")

@router.get("/notifications", response_model=List[dict])
async def get_chat_notifications(
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get chat notifications for current user."""
    try:
        notifications = await chat_service.get_user_notifications(current_user["sub"])
        return notifications
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting notifications: {str(e)}")


@router.post("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Mark a notification as read."""
    try:
        success = await chat_service.mark_notification_read(notification_id)
        
        return {
            "success": success,
            "message": "Notification marked as read" if success else "Notification not found"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error marking notification as read: {str(e)}")