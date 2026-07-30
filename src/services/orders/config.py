"""Order service configuration."""

from typing import Optional


class OrderServiceConfig:
    """Order service configuration settings."""
    
    def __init__(self):
        # Cart Configuration
        self.cart_expiry_days: int = 30
        self.max_cart_items: int = 100
        self.max_item_quantity: int = 999
        
        # Order Configuration
        self.order_timeout_minutes: int = 15
        self.max_order_items: int = 50
        
        # Tracking Configuration
        self.tracking_number_prefix: str = "MP"
        self.tracking_number_length: int = 12
        
        # Status Configuration
        self.auto_confirm_orders: bool = True
        self.auto_confirm_delay_minutes: int = 5


# Global configuration instance
order_config = OrderServiceConfig()