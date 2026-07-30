"""Notification service configuration."""

from typing import Optional, List


class NotificationServiceConfig:
    """Notification service configuration settings."""
    
    def __init__(self):
        # Email Configuration
        self.smtp_host: str = "smtp.gmail.com"
        self.smtp_port: int = 587
        self.smtp_username: str = "your-email@gmail.com"
        self.smtp_password: str = "your-app-password"
        self.smtp_use_tls: bool = True
        
        # Template Configuration
        self.email_template_path: str = "templates/email/"
        self.default_sender_email: str = "noreply@marketplace.com"
        self.default_sender_name: str = "Marketplace Platform"
        
        # Notification Configuration
        self.max_notifications_per_user: int = 1000
        self.notification_retention_days: int = 90
        self.batch_size: int = 100
        
        # Rate Limiting
        self.max_emails_per_hour: int = 100
        self.max_notifications_per_minute: int = 10
        
        # Retry Configuration
        self.max_retry_attempts: int = 3
        self.retry_delay_seconds: int = 60


# Global configuration instance
notification_config = NotificationServiceConfig()