"""Payment service configuration."""

from typing import Optional, List


class PaymentServiceConfig:
    """Payment service configuration settings."""
    
    def __init__(self):
        # Payment Gateway Configuration
        self.payment_gateway_url: str = "https://api.stripe.com"
        self.payment_gateway_key: str = "sk_test_your_stripe_key"
        self.payment_gateway_timeout: int = 30
        
        # Payment Configuration
        self.supported_currencies: List[str] = ["USD", "EUR", "GBP"]
        self.min_payment_amount: float = 0.50
        self.max_payment_amount: float = 10000.00
        
        # Security Configuration
        self.encryption_key: str = "your-encryption-key-here"
        self.payment_data_retention_days: int = 365
        
        # Retry Configuration
        self.max_payment_retries: int = 3
        self.retry_delay_seconds: int = 5
        
        # Receipt Configuration
        self.receipt_template_path: str = "templates/receipt.html"


# Global configuration instance
payment_config = PaymentServiceConfig()