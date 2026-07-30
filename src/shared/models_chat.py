"""Chat models for buyer-seller communication."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class MessageStatus(Enum):
    """Message status enumeration."""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    BLOCKED = "blocked"  # Message blocked by content filter


@dataclass
class ChatMessage:
    """Chat message model."""
    id: str
    product_id: str
    sender_id: str
    receiver_id: str
    message: str
    original_message: Optional[str] = None  # Original message before filtering
    status: MessageStatus = MessageStatus.SENT
    is_filtered: bool = False
    filter_reason: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class ProductChat:
    """Product chat conversation model."""
    id: str
    product_id: str
    buyer_id: str
    seller_id: str
    messages: List[ChatMessage]
    last_message_at: datetime
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()


@dataclass
class ChatFilter:
    """Chat content filter configuration."""
    blocked_patterns: List[str]
    warning_patterns: List[str]
    replacement_text: str = "[INFORMACIÓN BLOQUEADA]"
    
    @classmethod
    def get_default_filter(cls) -> 'ChatFilter':
        """Get default chat filter with common patterns."""
        return cls(
            blocked_patterns=[
                # Email patterns
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                # Phone patterns (Colombian and international)
                r'\b(?:\+?57\s?)?(?:3[0-9]{2}|[1-8][0-9]{2})\s?[0-9]{3}\s?[0-9]{4}\b',
                r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
                r'\b\d{10,15}\b',
                # WhatsApp patterns
                r'\bwhatsapp\b',
                r'\bwsp\b',
                r'\bwa\.me\b',
                # Social media
                r'\binstagram\b',
                r'\bfacebook\b',
                r'\btelegram\b',
                r'\btiktok\b',
                # URLs
                r'https?://[^\s]+',
                r'www\.[^\s]+',
                r'\b[a-zA-Z0-9-]+\.(com|co|net|org|edu|gov|mil|int|info|biz|name|museum|coop|aero|[a-z]{2})\b',
                # Contact info
                r'\bcontact[ao]me\b',
                r'\bllam[ae]me\b',
                r'\bescr[ií]beme\b',
                r'\bmensaje\s+privado\b',
                r'\bfuera\s+de\s+aqu[ií]\b',
                r'\bpor\s+fuera\b',
            ],
            warning_patterns=[
                r'\bprecio\s+fuera\b',
                r'\bpago\s+directo\b',
                r'\bsin\s+comisi[oó]n\b',
                r'\bevitar\s+comisi[oó]n\b',
            ]
        )