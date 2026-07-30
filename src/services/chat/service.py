"""Chat service for buyer-seller communication."""

import uuid
import re
from typing import List, Optional, Tuple
from datetime import datetime

from ...shared.models_chat import ChatMessage, ProductChat, MessageStatus, ChatFilter


class ChatService:
    """Service for managing product chats between buyers and sellers."""
    
    def __init__(self, product_service=None):
        """Initialize chat service."""
        # In-memory storage (will be replaced with database later)
        self._chats: dict[str, ProductChat] = {}
        self._messages: dict[str, ChatMessage] = {}
        self._filter = ChatFilter.get_default_filter()
        self._product_service = product_service
    
    async def get_or_create_chat(self, product_id: str, buyer_id: str, seller_id: str) -> ProductChat:
        """
        Get existing chat or create new one for a product.
        
        Args:
            product_id: Product ID
            buyer_id: Buyer user ID
            seller_id: Seller user ID
            
        Returns:
            ProductChat instance
        """
        # Look for existing chat
        for chat in self._chats.values():
            if (chat.product_id == product_id and 
                chat.buyer_id == buyer_id and 
                chat.seller_id == seller_id):
                return chat
        
        # Create new chat
        chat_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        chat = ProductChat(
            id=chat_id,
            product_id=product_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            messages=[],
            last_message_at=now,
            created_at=now,
            updated_at=now
        )
        
        self._chats[chat_id] = chat
        return chat
    
    async def send_message(self, product_id: str, sender_id: str, receiver_id: str, message: str) -> Tuple[ChatMessage, bool]:
        """
        Send a message in a product chat.
        
        Args:
            product_id: Product ID
            sender_id: Sender user ID
            receiver_id: Receiver user ID
            message: Message content
            
        Returns:
            Tuple of (ChatMessage, is_blocked)
        """
        # Get product information to determine seller
        seller_id = receiver_id  # Assume receiver is seller for now
        buyer_id = sender_id     # Assume sender is buyer for now
        
        # If we have access to product service, get the actual seller_id
        if self._product_service:
            try:
                product = await self._product_service.get_product_by_id(product_id)
                if product:
                    actual_seller_id = product.seller_id
                    # Determine who is buyer and who is seller
                    if sender_id == actual_seller_id:
                        seller_id = sender_id
                        buyer_id = receiver_id
                    else:
                        seller_id = actual_seller_id
                        buyer_id = sender_id
            except Exception as e:
                print(f"Warning: Could not get product info: {e}")
        
        # Get or create chat
        chat = await self.get_or_create_chat(product_id, buyer_id, seller_id)
        
        # Filter message content
        filtered_message, is_blocked, filter_reason = self._filter_message(message)
        
        # Create message
        message_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        chat_message = ChatMessage(
            id=message_id,
            product_id=product_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message=filtered_message,
            original_message=message if is_blocked else None,
            status=MessageStatus.BLOCKED if is_blocked else MessageStatus.SENT,
            is_filtered=is_blocked,
            filter_reason=filter_reason,
            created_at=now,
            updated_at=now
        )
        
        # Store message
        self._messages[message_id] = chat_message
        
        # Add to chat
        chat.messages.append(chat_message)
        chat.last_message_at = now
        chat.updated_at = now
        
        # Create notification for receiver (only if message is not blocked)
        if not is_blocked:
            await self._create_chat_notification(chat_message)
        
        return chat_message, is_blocked
    
    async def get_chat_messages(self, product_id: str, user_id: str) -> List[ChatMessage]:
        """
        Get all messages for a product chat involving the user.
        
        Args:
            product_id: Product ID
            user_id: User ID (buyer or seller)
            
        Returns:
            List of chat messages
        """
        messages = []
        
        for chat in self._chats.values():
            if (chat.product_id == product_id and 
                (chat.buyer_id == user_id or chat.seller_id == user_id)):
                # Return only non-blocked messages
                messages.extend([msg for msg in chat.messages if msg.status != MessageStatus.BLOCKED])
                break
        
        return sorted(messages, key=lambda x: x.created_at)
    
    async def get_user_chats(self, user_id: str) -> List[ProductChat]:
        """
        Get all chats for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of product chats
        """
        user_chats = []
        
        for chat in self._chats.values():
            if chat.buyer_id == user_id or chat.seller_id == user_id:
                user_chats.append(chat)
        
        return sorted(user_chats, key=lambda x: x.last_message_at, reverse=True)
    
    async def mark_messages_as_read(self, product_id: str, user_id: str) -> int:
        """
        Mark all messages in a chat as read by the user.
        
        Args:
            product_id: Product ID
            user_id: User ID
            
        Returns:
            Number of messages marked as read
        """
        marked_count = 0
        
        for chat in self._chats.values():
            if (chat.product_id == product_id and 
                (chat.buyer_id == user_id or chat.seller_id == user_id)):
                
                for message in chat.messages:
                    if (message.receiver_id == user_id and 
                        message.status == MessageStatus.SENT):
                        message.status = MessageStatus.READ
                        message.updated_at = datetime.utcnow()
                        marked_count += 1
                break
        
        return marked_count
    
    def _filter_message(self, message: str) -> Tuple[str, bool, Optional[str]]:
        """
        Filter message content for blocked patterns.
        
        Args:
            message: Original message
            
        Returns:
            Tuple of (filtered_message, is_blocked, filter_reason)
        """
        original_message = message
        is_blocked = False
        filter_reason = None
        
        # Check for blocked patterns
        for pattern in self._filter.blocked_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                message = re.sub(pattern, self._filter.replacement_text, message, flags=re.IGNORECASE)
                is_blocked = True
                filter_reason = "Información de contacto detectada"
        
        # Check for warning patterns
        for pattern in self._filter.warning_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                if not filter_reason:
                    filter_reason = "Contenido sospechoso detectado"
        
        return message, is_blocked, filter_reason
    
    async def get_chat_stats(self, product_id: str) -> dict:
        """
        Get chat statistics for a product.
        
        Args:
            product_id: Product ID
            
        Returns:
            Dictionary with chat statistics
        """
        stats = {
            "total_chats": 0,
            "total_messages": 0,
            "blocked_messages": 0,
            "active_chats": 0
        }
        
        for chat in self._chats.values():
            if chat.product_id == product_id:
                stats["total_chats"] += 1
                if chat.is_active:
                    stats["active_chats"] += 1
                
                for message in chat.messages:
                    stats["total_messages"] += 1
                    if message.status == MessageStatus.BLOCKED:
                        stats["blocked_messages"] += 1
        
        return stats
    
    async def _create_chat_notification(self, message: ChatMessage):
        """
        Create notification for new chat message.
        
        Args:
            message: Chat message that triggered the notification
        """
        # This is a simplified notification system
        # In a real implementation, you'd integrate with a proper notification service
        
        # Store notification in memory (simple implementation)
        if not hasattr(self, '_notifications'):
            self._notifications = {}
        
        notification_id = str(uuid.uuid4())
        notification = {
            'id': notification_id,
            'user_id': message.receiver_id,
            'type': 'chat_message',
            'title': 'Nueva pregunta sobre tu producto',
            'message': f'Tienes una nueva pregunta sobre tu producto',
            'data': {
                'product_id': message.product_id,
                'sender_id': message.sender_id,
                'message_preview': message.message[:50] + '...' if len(message.message) > 50 else message.message
            },
            'is_read': False,
            'created_at': datetime.utcnow()
        }
        
        self._notifications[notification_id] = notification
    
    async def get_user_notifications(self, user_id: str) -> List[dict]:
        """
        Get notifications for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of notifications
        """
        if not hasattr(self, '_notifications'):
            return []
        
        user_notifications = []
        for notification in self._notifications.values():
            if notification['user_id'] == user_id:
                user_notifications.append(notification)
        
        # Sort by creation date (newest first)
        return sorted(user_notifications, key=lambda x: x['created_at'], reverse=True)
    
    async def mark_notification_read(self, notification_id: str) -> bool:
        """
        Mark notification as read.
        
        Args:
            notification_id: Notification ID
            
        Returns:
            True if marked successfully, False otherwise
        """
        if hasattr(self, '_notifications') and notification_id in self._notifications:
            self._notifications[notification_id]['is_read'] = True
            return True
        return False