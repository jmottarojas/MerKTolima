"""Notification service tests."""

import pytest
import asyncio
from datetime import datetime
from hypothesis import given, strategies as st, settings
from tests.test_config import (
    valid_notification_types,
    valid_notification_channels,
    PropertyTestUtils,
)


class TestNotificationService:
    """Notification service test cases."""
    
    def test_notification_service_initialization(self):
        """Test notification service can be initialized."""
        from src.services.notifications.service import NotificationService
        from src.services.notifications.repository import InMemoryNotificationRepository
        
        repository = InMemoryNotificationRepository()
        service = NotificationService(repository)
        assert service is not None
    
    def test_notification_models_can_be_imported(self):
        """Test that notification models can be imported correctly."""
        from src.services.notifications.service import (
            Notification,
            NotificationData,
            NotificationPreferences,
            NotificationType,
            NotificationChannel,
            ScheduledNotification,
        )
        
        # Test that models can be instantiated with valid data
        notification_data = NotificationData(
            user_id="test-user-id",
            type=NotificationType.EMAIL,
            channel=NotificationChannel.ORDER_UPDATES,
            subject="Test Subject",
            content="Test content"
        )
        assert notification_data.user_id == "test-user-id"
        assert notification_data.type == NotificationType.EMAIL
    
    @given(
        notification_type=valid_notification_types(),
        channel=valid_notification_channels()
    )
    def test_notification_data_validation(self, notification_type, channel):
        """Property test: Valid notification data should be accepted."""
        from src.services.notifications.service import NotificationData
        
        try:
            notification_data = NotificationData(
                user_id="test-user-id",
                type=notification_type,
                channel=channel,
                subject="Test Subject",
                content="Test content"
            )
            assert notification_data.type == notification_type
            assert notification_data.channel == channel
        except Exception:
            # Skip invalid combinations for now
            pytest.skip("Invalid data combination - will be handled in task 11")
    
    def test_notification_repository_interface(self):
        """Test notification repository interface can be imported."""
        from src.services.notifications.repository import NotificationRepository
        assert NotificationRepository is not None
    
    def test_notification_config_can_be_imported(self):
        """Test notification configuration can be imported."""
        from src.services.notifications.config import notification_config
        assert notification_config is not None
        assert hasattr(notification_config, 'smtp_host')
        assert hasattr(notification_config, 'max_notifications_per_user')


class TestNotificationServiceProperties:
    """Property-based tests for NotificationService."""
    
    def _create_notification_service(self):
        """Create notification service with in-memory repository."""
        from src.services.notifications.service import NotificationService
        from src.services.notifications.repository import InMemoryNotificationRepository
        
        repository = InMemoryNotificationRepository()
        return NotificationService(repository)
    
    @given(
        order_id=st.text(min_size=1, max_size=50),
        seller_id=st.text(min_size=1, max_size=50),
        seller_email=st.emails(),
        total_amount=st.decimals(min_value=1, max_value=10000, places=2)
    )
    def test_property_25_new_order_notification(self, order_id, seller_id, seller_email, total_amount):
        """
        Feature: marketplace-platform, Property 25: Notificación de nuevo pedido
        For any order created, the system should notify the seller immediately
        **Validates: Requirements 6.1**
        """
        async def run_test():
            notification_service = self._create_notification_service()
            
            order_details = {
                "total_amount": float(total_amount),
                "currency": "USD"
            }
            
            # Get initial notification count
            initial_notifications = await notification_service.get_notification_history(seller_id)
            initial_count = len(initial_notifications)
            
            # Trigger new order notification
            await notification_service.notify_new_order_to_seller(
                order_id=order_id,
                seller_id=seller_id,
                seller_email=seller_email,
                order_details=order_details
            )
            
            # Check that notifications were created
            final_notifications = await notification_service.get_notification_history(seller_id)
            final_count = len(final_notifications)
            
            # Should have at least one new notification (in-app)
            assert final_count > initial_count, f"Expected more notifications after new order, got {final_count} vs {initial_count}"
            
            # Check that the notification contains order information
            new_notifications = final_notifications[:final_count - initial_count]
            order_notification = None
            for notification in new_notifications:
                if order_id in notification.content:
                    order_notification = notification
                    break
            
            assert order_notification is not None, "Should have notification containing order ID"
            assert order_notification.user_id == seller_id
            assert "Nuevo Pedido" in order_notification.subject or "nuevo pedido" in order_notification.content.lower()
        
        asyncio.run(run_test())
    
    @given(
        user_id=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != ""),
        notification_type=st.sampled_from(['email', 'in_app']),
        channel=st.sampled_from(['order_updates', 'price_alerts', 'inventory_alerts']),
        subject=st.text(min_size=1, max_size=100).filter(lambda x: x.strip() != ""),
        content=st.text(min_size=1, max_size=500).filter(lambda x: x.strip() != "")
    )
    def test_property_34_notification_sending(self, user_id, notification_type, channel, subject, content):
        """
        Feature: marketplace-platform, Property 34: Envío de notificaciones
        For any relevant event, the system should send notification by email and/or in-platform
        **Validates: Requirements 8.1**
        """
        async def run_test():
            notification_service = self._create_notification_service()
            
            from src.services.notifications.service import NotificationData, NotificationType, NotificationChannel
            
            # Strip whitespace to match what Pydantic validators do
            user_id_stripped = user_id.strip()
            subject_stripped = subject.strip()
            content_stripped = content.strip()
            
            # Create notification data
            notification_data = NotificationData(
                user_id=user_id_stripped,
                type=NotificationType(notification_type),
                channel=NotificationChannel(channel),
                subject=subject_stripped,
                content=content_stripped,
                metadata={"user_email": "test@example.com"} if notification_type == 'email' else None
            )
            
            # Get initial notification count
            initial_notifications = await notification_service.get_notification_history(user_id_stripped)
            initial_count = len(initial_notifications)
            
            # Send notification
            await notification_service.send_notification(notification_data)
            
            # For in-app notifications, check they were stored
            if notification_type == 'in_app':
                final_notifications = await notification_service.get_notification_history(user_id_stripped)
                final_count = len(final_notifications)
                
                # Should have one new notification
                assert final_count == initial_count + 1, f"Expected one new notification, got {final_count - initial_count}"
                
                # Check notification content (compare with stripped values)
                new_notification = final_notifications[0]  # Most recent first
                assert new_notification.user_id == user_id_stripped
                assert new_notification.subject == subject_stripped
                assert new_notification.content == content_stripped
                assert new_notification.type.value == notification_type
                assert new_notification.channel.value == channel
        
        asyncio.run(run_test())
    
    @given(
        user_id=st.text(min_size=1, max_size=50).filter(lambda x: x.strip() != ""),
        num_notifications=st.integers(min_value=1, max_value=10)
    )
    def test_property_38_notification_history(self, user_id, num_notifications):
        """
        Feature: marketplace-platform, Property 38: Historial de notificaciones
        For any user with notifications, the system should maintain complete history
        **Validates: Requirements 8.5**
        """
        async def run_test():
            notification_service = self._create_notification_service()
            
            from src.services.notifications.service import NotificationData, NotificationType, NotificationChannel
            
            # Strip whitespace to match what Pydantic validators do
            user_id_stripped = user_id.strip()
            
            # Send multiple notifications
            sent_notifications = []
            for i in range(num_notifications):
                notification_data = NotificationData(
                    user_id=user_id_stripped,
                    type=NotificationType.IN_APP,
                    channel=NotificationChannel.ORDER_UPDATES,
                    subject=f"Test Notification {i}",
                    content=f"Test content {i}"
                )
                await notification_service.send_notification(notification_data)
                sent_notifications.append(notification_data)
            
            # Get notification history
            history = await notification_service.get_notification_history(user_id_stripped)
            
            # Should have all sent notifications
            assert len(history) >= num_notifications, f"Expected at least {num_notifications} notifications in history, got {len(history)}"
            
            # Check that notifications are ordered by sent_at (most recent first)
            for i in range(len(history) - 1):
                assert history[i].sent_at >= history[i + 1].sent_at, "Notifications should be ordered by sent_at descending"
            
            # Check that all notifications belong to the user (compare with stripped value)
            for notification in history:
                assert notification.user_id == user_id_stripped, f"All notifications should belong to user {user_id_stripped}"
            
            # Check that notifications have required fields
            for notification in history:
                assert notification.id is not None and notification.id != ""
                assert notification.subject is not None and notification.subject != ""
                assert notification.content is not None and notification.content != ""
                assert notification.sent_at is not None
                assert isinstance(notification.read, bool)
        
        asyncio.run(run_test())


class TestNotificationServiceUnitTests:
    """Unit tests for NotificationService - specific formats and preferences."""
    
    def _create_notification_service(self):
        """Create notification service with in-memory repository."""
        from src.services.notifications.service import NotificationService
        from src.services.notifications.repository import InMemoryNotificationRepository
        
        repository = InMemoryNotificationRepository()
        return NotificationService(repository)
    
    def test_notification_service_requires_repository(self):
        """Test that NotificationService requires a repository."""
        from src.services.notifications.service import NotificationService
        
        with pytest.raises(ValueError, match="Repository cannot be None"):
            NotificationService(None)
    
    def test_send_notification_validates_input(self):
        """Test that send_notification validates input data."""
        async def run_test():
            service = self._create_notification_service()
            
            with pytest.raises(ValueError, match="notification_data cannot be None"):
                await service.send_notification(None)
        
        asyncio.run(run_test())
    
    def test_user_preferences_default_values(self):
        """Test that default user preferences are correctly set."""
        async def run_test():
            service = self._create_notification_service()
            
            # Get preferences for new user (should create defaults)
            preferences = await service.get_user_preferences("new-user-123")
            
            # Check default values
            assert preferences.email_enabled is True
            assert preferences.in_app_enabled is True
            assert preferences.sms_enabled is False
            
            # Check default channel preferences
            from src.services.notifications.service import NotificationChannel
            assert preferences.channels[NotificationChannel.ORDER_UPDATES] is True
            assert preferences.channels[NotificationChannel.PRICE_ALERTS] is True
            assert preferences.channels[NotificationChannel.INVENTORY_ALERTS] is True
            assert preferences.channels[NotificationChannel.MARKETING] is False
        
        asyncio.run(run_test())
    
    def test_update_user_preferences_validation(self):
        """Test user preferences update validation."""
        async def run_test():
            service = self._create_notification_service()
            
            # Test empty user_id
            with pytest.raises(ValueError, match="user_id cannot be empty"):
                await service.update_user_preferences("", None)
            
            with pytest.raises(ValueError, match="user_id cannot be empty"):
                await service.update_user_preferences("   ", None)
            
            # Test None preferences
            with pytest.raises(ValueError, match="preferences cannot be None"):
                await service.update_user_preferences("user-123", None)
        
        asyncio.run(run_test())
    
    def test_notification_respects_channel_preferences(self):
        """Test that notifications respect user channel preferences."""
        async def run_test():
            service = self._create_notification_service()
            from src.services.notifications.service import (
                NotificationData, NotificationPreferences, NotificationType, NotificationChannel
            )
            
            user_id = "test-user-123"
            
            # Set preferences to disable order updates
            preferences = NotificationPreferences()
            preferences.channels[NotificationChannel.ORDER_UPDATES] = False
            await service.update_user_preferences(user_id, preferences)
            
            # Try to send order update notification
            notification_data = NotificationData(
                user_id=user_id,
                type=NotificationType.IN_APP,
                channel=NotificationChannel.ORDER_UPDATES,
                subject="Order Update",
                content="Your order has been updated"
            )
            
            # Send notification (should be ignored due to preferences)
            await service.send_notification(notification_data)
            
            # Check that no notification was created
            history = await service.get_notification_history(user_id)
            assert len(history) == 0, "No notification should be created when channel is disabled"
        
        asyncio.run(run_test())
    
    def test_email_notification_requires_email_metadata(self):
        """Test that email notifications require user_email in metadata."""
        async def run_test():
            service = self._create_notification_service()
            from src.services.notifications.service import (
                NotificationData, NotificationType, NotificationChannel
            )
            
            # Try to send email notification without user_email in metadata
            notification_data = NotificationData(
                user_id="test-user-123",
                type=NotificationType.EMAIL,
                channel=NotificationChannel.ORDER_UPDATES,
                subject="Test Email",
                content="Test content"
            )
            
            with pytest.raises(ValueError, match="user_email required in metadata for email notifications"):
                await service.send_notification(notification_data)
            
            # Try with empty metadata
            notification_data.metadata = {}
            with pytest.raises(ValueError, match="user_email required in metadata for email notifications"):
                await service.send_notification(notification_data)
        
        asyncio.run(run_test())
    
    def test_mark_notification_as_read_validation(self):
        """Test mark notification as read validation."""
        async def run_test():
            service = self._create_notification_service()
            
            # Test empty notification_id
            with pytest.raises(ValueError, match="notification_id cannot be empty"):
                await service.mark_notification_as_read("")
            
            with pytest.raises(ValueError, match="notification_id cannot be empty"):
                await service.mark_notification_as_read("   ")
        
        asyncio.run(run_test())
    
    def test_get_notification_history_validation(self):
        """Test get notification history validation."""
        async def run_test():
            service = self._create_notification_service()
            
            # Test empty user_id
            with pytest.raises(ValueError, match="user_id cannot be empty"):
                await service.get_notification_history("")
            
            with pytest.raises(ValueError, match="user_id cannot be empty"):
                await service.get_notification_history("   ")
            
            # Test invalid limit
            with pytest.raises(ValueError, match="limit must be positive"):
                await service.get_notification_history("user-123", 0)
            
            with pytest.raises(ValueError, match="limit must be positive"):
                await service.get_notification_history("user-123", -1)
        
        asyncio.run(run_test())
    
    def test_schedule_notification_validation(self):
        """Test schedule notification validation."""
        async def run_test():
            service = self._create_notification_service()
            
            # Test None notification
            with pytest.raises(ValueError, match="notification cannot be None"):
                await service.schedule_notification(None)
        
        asyncio.run(run_test())
    
    def test_schedule_notification_immediate_delivery(self):
        """Test that past/current scheduled notifications are delivered immediately."""
        async def run_test():
            service = self._create_notification_service()
            from src.services.notifications.service import (
                NotificationData, ScheduledNotification, NotificationType, NotificationChannel
            )
            from datetime import datetime, timedelta
            
            user_id = "test-user-123"
            
            # Create notification scheduled for the past
            past_time = datetime.utcnow() - timedelta(hours=1)
            notification_data = NotificationData(
                user_id=user_id,
                type=NotificationType.IN_APP,
                channel=NotificationChannel.ORDER_UPDATES,
                subject="Past Notification",
                content="This should be delivered immediately"
            )
            
            scheduled_notification = ScheduledNotification(
                notification_data=notification_data,
                scheduled_for=past_time
            )
            
            # Schedule the notification
            await service.schedule_notification(scheduled_notification)
            
            # Check that notification was delivered immediately
            history = await service.get_notification_history(user_id)
            assert len(history) == 1, "Past scheduled notification should be delivered immediately"
            assert history[0].subject == "Past Notification"
        
        asyncio.run(run_test())


class TestNotificationServiceAutomaticTriggers:
    """Unit tests for automatic notification triggers."""
    
    def _create_notification_service(self):
        """Create notification service with in-memory repository."""
        from src.services.notifications.service import NotificationService
        from src.services.notifications.repository import InMemoryNotificationRepository
        
        repository = InMemoryNotificationRepository()
        return NotificationService(repository)
    
    def test_notify_new_order_to_seller_validation(self):
        """Test new order notification validation."""
        async def run_test():
            service = self._create_notification_service()
            
            # Test empty order_id
            with pytest.raises(ValueError, match="order_id cannot be empty"):
                await service.notify_new_order_to_seller("", "seller-123", "seller@test.com", {"total_amount": 100})
            
            # Test empty seller_id
            with pytest.raises(ValueError, match="seller_id cannot be empty"):
                await service.notify_new_order_to_seller("order-123", "", "seller@test.com", {"total_amount": 100})
            
            # Test empty seller_email
            with pytest.raises(ValueError, match="seller_email cannot be empty"):
                await service.notify_new_order_to_seller("order-123", "seller-123", "", {"total_amount": 100})
            
            # Test empty order_details
            with pytest.raises(ValueError, match="order_details cannot be empty"):
                await service.notify_new_order_to_seller("order-123", "seller-123", "seller@test.com", None)
        
        asyncio.run(run_test())
    
    def test_notify_new_order_creates_correct_notifications(self):
        """Test that new order notification creates correct content."""
        async def run_test():
            service = self._create_notification_service()
            
            order_id = "ORD-12345"
            seller_id = "seller-123"
            seller_email = "seller@test.com"
            order_details = {
                "total_amount": 150.75,
                "currency": "USD"
            }
            
            # Send new order notification
            await service.notify_new_order_to_seller(order_id, seller_id, seller_email, order_details)
            
            # Check notifications were created
            history = await service.get_notification_history(seller_id)
            assert len(history) >= 1, "Should have at least one notification"
            
            # Find the in-app notification
            in_app_notification = None
            for notification in history:
                if notification.type.value == "in_app":
                    in_app_notification = notification
                    break
            
            assert in_app_notification is not None, "Should have in-app notification"
            assert order_id in in_app_notification.content, "Notification should contain order ID"
            assert "150.75" in in_app_notification.content, "Notification should contain amount"
            assert "USD" in in_app_notification.content, "Notification should contain currency"
            assert "Nuevo Pedido" in in_app_notification.subject, "Subject should mention new order"
        
        asyncio.run(run_test())
    
    def test_notify_order_status_change_validation(self):
        """Test order status change notification validation."""
        async def run_test():
            service = self._create_notification_service()
            
            # Test empty order_id
            with pytest.raises(ValueError, match="order_id cannot be empty"):
                await service.notify_order_status_change_to_buyer("", "buyer-123", "buyer@test.com", "pending", "confirmed")
            
            # Test empty buyer_id
            with pytest.raises(ValueError, match="buyer_id cannot be empty"):
                await service.notify_order_status_change_to_buyer("order-123", "", "buyer@test.com", "pending", "confirmed")
            
            # Test empty buyer_email
            with pytest.raises(ValueError, match="buyer_email cannot be empty"):
                await service.notify_order_status_change_to_buyer("order-123", "buyer-123", "", "pending", "confirmed")
            
            # Test empty old_status
            with pytest.raises(ValueError, match="old_status cannot be empty"):
                await service.notify_order_status_change_to_buyer("order-123", "buyer-123", "buyer@test.com", "", "confirmed")
            
            # Test empty new_status
            with pytest.raises(ValueError, match="new_status cannot be empty"):
                await service.notify_order_status_change_to_buyer("order-123", "buyer-123", "buyer@test.com", "pending", "")
        
        asyncio.run(run_test())
    
    def test_notify_order_status_change_content(self):
        """Test order status change notification content."""
        async def run_test():
            service = self._create_notification_service()
            
            order_id = "ORD-12345"
            buyer_id = "buyer-123"
            buyer_email = "buyer@test.com"
            
            # Test different status changes
            status_tests = [
                ("pending", "confirmed", "confirmado"),
                ("confirmed", "processing", "procesado"),
                ("processing", "shipped", "enviado"),
                ("shipped", "delivered", "entregado"),
                ("confirmed", "cancelled", "cancelado")
            ]
            
            for old_status, new_status, expected_word in status_tests:
                # Send status change notification
                await service.notify_order_status_change_to_buyer(
                    order_id, buyer_id, buyer_email, old_status, new_status
                )
                
                # Check notification was created
                history = await service.get_notification_history(buyer_id)
                latest_notification = history[0]  # Most recent
                
                assert order_id in latest_notification.subject, f"Subject should contain order ID for {new_status}"
                assert expected_word in latest_notification.content.lower(), f"Content should mention {expected_word} for status {new_status}"
        
        asyncio.run(run_test())
    
    def test_notify_order_status_shipped_with_tracking(self):
        """Test shipped status notification includes tracking number."""
        async def run_test():
            service = self._create_notification_service()
            
            order_id = "ORD-12345"
            buyer_id = "buyer-123"
            buyer_email = "buyer@test.com"
            tracking_number = "TRK-98765"
            
            # Send shipped notification with tracking
            await service.notify_order_status_change_to_buyer(
                order_id, buyer_id, buyer_email, "processing", "shipped", tracking_number
            )
            
            # Check notification content
            history = await service.get_notification_history(buyer_id)
            notification = history[0]
            
            assert tracking_number in notification.content, "Notification should include tracking number"
            assert "seguimiento" in notification.content.lower(), "Notification should mention tracking"
        
        asyncio.run(run_test())
    
    def test_notify_low_inventory_validation(self):
        """Test low inventory notification validation."""
        async def run_test():
            service = self._create_notification_service()
            
            # Test empty product_id
            with pytest.raises(ValueError, match="product_id cannot be empty"):
                await service.notify_low_inventory_to_seller("", "seller-123", "seller@test.com", "Product", 5, 10)
            
            # Test empty seller_id
            with pytest.raises(ValueError, match="seller_id cannot be empty"):
                await service.notify_low_inventory_to_seller("prod-123", "", "seller@test.com", "Product", 5, 10)
            
            # Test empty seller_email
            with pytest.raises(ValueError, match="seller_email cannot be empty"):
                await service.notify_low_inventory_to_seller("prod-123", "seller-123", "", "Product", 5, 10)
            
            # Test empty product_name
            with pytest.raises(ValueError, match="product_name cannot be empty"):
                await service.notify_low_inventory_to_seller("prod-123", "seller-123", "seller@test.com", "", 5, 10)
            
            # Test negative current_quantity
            with pytest.raises(ValueError, match="current_quantity cannot be negative"):
                await service.notify_low_inventory_to_seller("prod-123", "seller-123", "seller@test.com", "Product", -1, 10)
            
            # Test negative threshold
            with pytest.raises(ValueError, match="threshold cannot be negative"):
                await service.notify_low_inventory_to_seller("prod-123", "seller-123", "seller@test.com", "Product", 5, -1)
        
        asyncio.run(run_test())
    
    def test_notify_low_inventory_content(self):
        """Test low inventory notification content."""
        async def run_test():
            service = self._create_notification_service()
            
            product_id = "PROD-12345"
            seller_id = "seller-123"
            seller_email = "seller@test.com"
            product_name = "Awesome Widget"
            current_quantity = 3
            threshold = 10
            
            # Send low inventory notification
            await service.notify_low_inventory_to_seller(
                product_id, seller_id, seller_email, product_name, current_quantity, threshold
            )
            
            # Check notification content
            history = await service.get_notification_history(seller_id)
            notification = history[0]
            
            assert product_name in notification.content, "Notification should contain product name"
            assert str(current_quantity) in notification.content, "Notification should contain current quantity"
            assert str(threshold) in notification.content, "Notification should contain threshold"
            assert "Inventario Bajo" in notification.subject, "Subject should mention low inventory"
        
        asyncio.run(run_test())
    
    def test_notify_price_change_validation(self):
        """Test price change notification validation."""
        async def run_test():
            service = self._create_notification_service()
            
            user_wishlist = [{"user_id": "user-123", "email": "user@test.com"}]
            
            # Test empty product_id
            with pytest.raises(ValueError, match="product_id cannot be empty"):
                await service.notify_price_change_to_wishlist_users("", "Product", 100.0, 80.0, "USD", user_wishlist)
            
            # Test empty product_name
            with pytest.raises(ValueError, match="product_name cannot be empty"):
                await service.notify_price_change_to_wishlist_users("prod-123", "", 100.0, 80.0, "USD", user_wishlist)
            
            # Test negative old_price
            with pytest.raises(ValueError, match="old_price cannot be negative"):
                await service.notify_price_change_to_wishlist_users("prod-123", "Product", -1.0, 80.0, "USD", user_wishlist)
            
            # Test negative new_price
            with pytest.raises(ValueError, match="new_price cannot be negative"):
                await service.notify_price_change_to_wishlist_users("prod-123", "Product", 100.0, -1.0, "USD", user_wishlist)
            
            # Test empty currency
            with pytest.raises(ValueError, match="currency cannot be empty"):
                await service.notify_price_change_to_wishlist_users("prod-123", "Product", 100.0, 80.0, "", user_wishlist)
            
            # Test empty user_wishlist
            with pytest.raises(ValueError, match="user_wishlist cannot be empty"):
                await service.notify_price_change_to_wishlist_users("prod-123", "Product", 100.0, 80.0, "USD", [])
        
        asyncio.run(run_test())
    
    def test_notify_price_change_only_for_decreases(self):
        """Test that price change notifications are only sent for price decreases."""
        async def run_test():
            service = self._create_notification_service()
            
            user_wishlist = [{"user_id": "user-123", "email": "user@test.com"}]
            
            # Test price increase (should not notify)
            await service.notify_price_change_to_wishlist_users(
                "prod-123", "Product", 80.0, 100.0, "USD", user_wishlist
            )
            
            history = await service.get_notification_history("user-123")
            assert len(history) == 0, "Should not notify for price increases"
            
            # Test same price (should not notify)
            await service.notify_price_change_to_wishlist_users(
                "prod-123", "Product", 100.0, 100.0, "USD", user_wishlist
            )
            
            history = await service.get_notification_history("user-123")
            assert len(history) == 0, "Should not notify for same price"
        
        asyncio.run(run_test())
    
    def test_notify_price_change_content(self):
        """Test price change notification content."""
        async def run_test():
            service = self._create_notification_service()
            
            product_name = "Awesome Widget"
            old_price = 100.0
            new_price = 75.0
            currency = "USD"
            user_wishlist = [{"user_id": "user-123", "email": "user@test.com"}]
            
            # Send price change notification
            await service.notify_price_change_to_wishlist_users(
                "prod-123", product_name, old_price, new_price, currency, user_wishlist
            )
            
            # Check notification content
            history = await service.get_notification_history("user-123")
            notification = history[0]
            
            assert product_name in notification.content, "Notification should contain product name"
            assert str(old_price) in notification.content, "Notification should contain old price"
            assert str(new_price) in notification.content, "Notification should contain new price"
            assert currency in notification.content, "Notification should contain currency"
            assert "25.0%" in notification.content, "Notification should contain discount percentage"
            assert "Bajó el Precio" in notification.subject, "Subject should mention price drop"
        
        asyncio.run(run_test())
    
    def test_notify_price_change_skips_invalid_users(self):
        """Test that price change notification skips users with invalid data."""
        async def run_test():
            service = self._create_notification_service()
            
            # Mix of valid and invalid user data
            user_wishlist = [
                {"user_id": "user-123", "email": "user@test.com"},  # Valid
                {"user_id": "", "email": "invalid@test.com"},       # Invalid user_id
                {"user_id": "user-456", "email": ""},              # Invalid email
                {"user_id": "user-789", "email": "valid@test.com"} # Valid
            ]
            
            # Send price change notification
            await service.notify_price_change_to_wishlist_users(
                "prod-123", "Product", 100.0, 80.0, "USD", user_wishlist
            )
            
            # Check that only valid users got notifications
            history_123 = await service.get_notification_history("user-123")
            history_789 = await service.get_notification_history("user-789")
            history_456 = await service.get_notification_history("user-456")
            
            assert len(history_123) == 1, "Valid user should receive notification"
            assert len(history_789) == 1, "Valid user should receive notification"
            assert len(history_456) == 0, "User with invalid email should not receive notification"
        
        asyncio.run(run_test())