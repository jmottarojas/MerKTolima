"""Payment service implementation."""

import uuid
import hashlib
import hmac
import json
import asyncio
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from decimal import Decimal
from enum import Enum
from cryptography.fernet import Fernet
import base64

from .config import payment_config
from ...shared.service_integration import event_bus, Event, EventType


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethodType(str, Enum):
    """Payment method types."""
    CARD = "card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


class CardDetails(BaseModel):
    """Credit card details."""
    card_number: str = Field(..., min_length=13, max_length=19)
    expiry_month: int = Field(..., ge=1, le=12)
    expiry_year: int = Field(..., ge=2024)
    cvv: str = Field(..., min_length=3, max_length=4)
    cardholder_name: str = Field(..., min_length=1, max_length=100)

    @validator('card_number')
    def validate_card_number(cls, v):
        # Remove spaces and validate format
        v = v.replace(' ', '')
        if not v.isdigit():
            raise ValueError('Card number must contain only digits')
        return v

    @validator('cvv')
    def validate_cvv(cls, v):
        if not v.isdigit():
            raise ValueError('CVV must contain only digits')
        return v


class PayPalDetails(BaseModel):
    """PayPal payment details."""
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    account_id: Optional[str] = None


class BankTransferDetails(BaseModel):
    """Bank transfer details."""
    account_number: str = Field(..., min_length=8, max_length=20)
    routing_number: str = Field(..., min_length=9, max_length=9)
    account_holder_name: str = Field(..., min_length=1, max_length=100)
    bank_name: str = Field(..., min_length=1, max_length=100)


class PaymentMethod(BaseModel):
    """Payment method model."""
    type: PaymentMethodType
    details: Dict[str, Any]  # Encrypted payment details

    @validator('details')
    def validate_details(cls, v, values):
        if 'type' not in values:
            return v
        
        # Skip validation if this is encrypted data
        if 'encrypted_data' in v:
            return v
        
        payment_type = values['type']
        if payment_type == PaymentMethodType.CARD:
            # Validate card details structure
            required_fields = ['card_number', 'expiry_month', 'expiry_year', 'cvv', 'cardholder_name']
            if not all(field in v for field in required_fields):
                raise ValueError(f'Card payment requires: {required_fields}')
        elif payment_type == PaymentMethodType.PAYPAL:
            if 'email' not in v:
                raise ValueError('PayPal payment requires email')
        elif payment_type == PaymentMethodType.BANK_TRANSFER:
            required_fields = ['account_number', 'routing_number', 'account_holder_name', 'bank_name']
            if not all(field in v for field in required_fields):
                raise ValueError(f'Bank transfer requires: {required_fields}')
        
        return v


class PaymentData(BaseModel):
    """Payment data model."""
    order_id: str = Field(..., min_length=1)
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    payment_method: PaymentMethod
    billing_address: Optional[Dict[str, str]] = None

    @validator('currency')
    def validate_currency(cls, v):
        if v not in payment_config.supported_currencies:
            raise ValueError(f'Currency {v} not supported. Supported: {payment_config.supported_currencies}')
        return v

    @validator('amount')
    def validate_amount(cls, v):
        if v < Decimal(str(payment_config.min_payment_amount)):
            raise ValueError(f'Amount must be at least {payment_config.min_payment_amount}')
        if v > Decimal(str(payment_config.max_payment_amount)):
            raise ValueError(f'Amount cannot exceed {payment_config.max_payment_amount}')
        return v


class PaymentResult(BaseModel):
    """Payment result model."""
    payment_id: str
    status: PaymentStatus
    transaction_id: Optional[str] = None
    message: Optional[str] = None
    processed_at: datetime = Field(default_factory=datetime.utcnow)
    gateway_response: Optional[Dict[str, Any]] = None


class Receipt(BaseModel):
    """Receipt model."""
    id: str
    payment_id: str
    order_id: str
    amount: Decimal
    currency: str
    payment_method_type: str
    issued_at: datetime
    receipt_number: str
    merchant_info: Dict[str, str] = Field(default_factory=dict)


class RefundResult(BaseModel):
    """Refund result model."""
    refund_id: str
    status: str
    amount: Decimal
    message: Optional[str] = None
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class PaymentGatewaySimulator:
    """Simulated payment gateway for testing."""
    
    def __init__(self):
        self.success_rate = 0.9  # 90% success rate for simulation
    
    async def process_card_payment(self, card_details: Dict[str, Any], amount: Decimal) -> Dict[str, Any]:
        """Simulate card payment processing."""
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Simulate different scenarios based on card number
        card_number = card_details.get('card_number', '')
        
        if card_number.endswith('0000'):
            # Simulate declined card
            return {
                'success': False,
                'transaction_id': None,
                'error_code': 'CARD_DECLINED',
                'message': 'Your card was declined'
            }
        elif card_number.endswith('1111'):
            # Simulate insufficient funds
            return {
                'success': False,
                'transaction_id': None,
                'error_code': 'INSUFFICIENT_FUNDS',
                'message': 'Insufficient funds'
            }
        else:
            # Simulate successful payment
            return {
                'success': True,
                'transaction_id': f'txn_{uuid.uuid4().hex[:12]}',
                'error_code': None,
                'message': 'Payment processed successfully'
            }
    
    async def process_paypal_payment(self, paypal_details: Dict[str, Any], amount: Decimal) -> Dict[str, Any]:
        """Simulate PayPal payment processing."""
        await asyncio.sleep(0.2)  # Simulate network delay
        
        email = paypal_details.get('email', '')
        
        if 'invalid' in email.lower():
            return {
                'success': False,
                'transaction_id': None,
                'error_code': 'INVALID_ACCOUNT',
                'message': 'PayPal account not found'
            }
        else:
            return {
                'success': True,
                'transaction_id': f'pp_{uuid.uuid4().hex[:12]}',
                'error_code': None,
                'message': 'PayPal payment processed successfully'
            }
    
    async def process_bank_transfer(self, bank_details: Dict[str, Any], amount: Decimal) -> Dict[str, Any]:
        """Simulate bank transfer processing."""
        await asyncio.sleep(0.3)  # Simulate network delay
        
        account_number = bank_details.get('account_number', '')
        
        if account_number.startswith('999'):
            return {
                'success': False,
                'transaction_id': None,
                'error_code': 'INVALID_ACCOUNT',
                'message': 'Invalid bank account'
            }
        else:
            return {
                'success': True,
                'transaction_id': f'bt_{uuid.uuid4().hex[:12]}',
                'error_code': None,
                'message': 'Bank transfer initiated successfully'
            }


class PaymentEncryption:
    """Payment data encryption utilities."""
    
    def __init__(self, encryption_key: str):
        # Generate a proper Fernet key from the provided key
        key_bytes = encryption_key.encode('utf-8')
        # Use SHA256 to create a 32-byte key, then base64 encode for Fernet
        hashed_key = hashlib.sha256(key_bytes).digest()
        fernet_key = base64.urlsafe_b64encode(hashed_key)
        self.cipher = Fernet(fernet_key)
    
    def encrypt_payment_details(self, details: Dict[str, Any]) -> str:
        """Encrypt sensitive payment details."""
        json_data = json.dumps(details, default=str)
        encrypted_data = self.cipher.encrypt(json_data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_payment_details(self, encrypted_details: str) -> Dict[str, Any]:
        """Decrypt payment details."""
        try:
            encrypted_data = base64.urlsafe_b64decode(encrypted_details.encode('utf-8'))
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode('utf-8'))
        except Exception as e:
            raise ValueError(f"Failed to decrypt payment details: {str(e)}")
    
    def mask_sensitive_data(self, details: Dict[str, Any], payment_type: PaymentMethodType) -> Dict[str, Any]:
        """Mask sensitive data for logging/display."""
        masked = details.copy()
        
        if payment_type == PaymentMethodType.CARD:
            if 'card_number' in masked:
                card_number = masked['card_number']
                masked['card_number'] = f"****-****-****-{card_number[-4:]}"
            if 'cvv' in masked:
                masked['cvv'] = "***"
        elif payment_type == PaymentMethodType.BANK_TRANSFER:
            if 'account_number' in masked:
                account = masked['account_number']
                masked['account_number'] = f"****{account[-4:]}"
        
        return masked


class PaymentService:
    """Payment service for processing payments."""
    
    def __init__(self, repository=None):
        """Initialize payment service."""
        self.repository = repository
        self.gateway = PaymentGatewaySimulator()
        self.encryption = PaymentEncryption(payment_config.encryption_key)
        self._payment_storage: Dict[str, PaymentResult] = {}
        self._receipt_storage: Dict[str, Receipt] = {}
    
    async def process_payment(self, payment_data: PaymentData) -> PaymentResult:
        """Process a payment with encryption and gateway integration."""
        payment_id = str(uuid.uuid4())
        
        try:
            # Validate payment method
            if not await self.validate_payment_method(payment_data.payment_method):
                return PaymentResult(
                    payment_id=payment_id,
                    status=PaymentStatus.FAILED,
                    message="Invalid payment method"
                )
            
            # Decrypt payment details for processing
            decrypted_details = self.encryption.decrypt_payment_details(
                payment_data.payment_method.details.get('encrypted_data', '{}')
            ) if 'encrypted_data' in payment_data.payment_method.details else payment_data.payment_method.details
            
            # Process payment based on method type
            gateway_response = await self._process_with_gateway(
                payment_data.payment_method.type,
                decrypted_details,
                payment_data.amount
            )
            
            # Create payment result
            if gateway_response['success']:
                result = PaymentResult(
                    payment_id=payment_id,
                    status=PaymentStatus.COMPLETED,
                    transaction_id=gateway_response['transaction_id'],
                    message=gateway_response['message'],
                    gateway_response=gateway_response
                )
            else:
                result = PaymentResult(
                    payment_id=payment_id,
                    status=PaymentStatus.FAILED,
                    message=gateway_response['message'],
                    gateway_response=gateway_response
                )
            
            # Store payment result
            self._payment_storage[payment_id] = result
            if self.repository:
                await self.repository.save_payment_result(result)
            
            # Publish payment events
            if result.status == PaymentStatus.COMPLETED:
                await event_bus.publish(Event(
                    type=EventType.PAYMENT_COMPLETED,
                    source_service="payment_service",
                    data={
                        "payment_id": payment_id,
                        "order_id": payment_data.order_id,
                        "amount": float(payment_data.amount),
                        "currency": payment_data.currency,
                        "transaction_id": result.transaction_id
                    }
                ))
            else:
                await event_bus.publish(Event(
                    type=EventType.PAYMENT_FAILED,
                    source_service="payment_service",
                    data={
                        "payment_id": payment_id,
                        "order_id": payment_data.order_id,
                        "amount": float(payment_data.amount),
                        "currency": payment_data.currency,
                        "error_message": result.message
                    }
                ))
            
            return result
            
        except Exception as e:
            error_result = PaymentResult(
                payment_id=payment_id,
                status=PaymentStatus.FAILED,
                message=f"Payment processing error: {str(e)}"
            )
            self._payment_storage[payment_id] = error_result
            return error_result
    
    async def _process_with_gateway(self, payment_type: PaymentMethodType, details: Dict[str, Any], amount: Decimal) -> Dict[str, Any]:
        """Process payment with appropriate gateway method."""
        if payment_type == PaymentMethodType.CARD:
            return await self.gateway.process_card_payment(details, amount)
        elif payment_type == PaymentMethodType.PAYPAL:
            return await self.gateway.process_paypal_payment(details, amount)
        elif payment_type == PaymentMethodType.BANK_TRANSFER:
            return await self.gateway.process_bank_transfer(details, amount)
        else:
            return {
                'success': False,
                'transaction_id': None,
                'error_code': 'UNSUPPORTED_METHOD',
                'message': f'Payment method {payment_type} not supported'
            }
    
    async def validate_payment_method(self, payment_method: PaymentMethod) -> bool:
        """Validate payment method details."""
        try:
            # Check if payment method type is supported
            if payment_method.type not in [PaymentMethodType.CARD, PaymentMethodType.PAYPAL, PaymentMethodType.BANK_TRANSFER]:
                return False
            
            # Validate details structure based on payment type
            details = payment_method.details
            
            if payment_method.type == PaymentMethodType.CARD:
                # Validate card details
                required_fields = ['card_number', 'expiry_month', 'expiry_year', 'cvv', 'cardholder_name']
                if not all(field in details for field in required_fields):
                    return False
                
                # Basic card number validation (Luhn algorithm could be added)
                card_number = details['card_number'].replace(' ', '')
                if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
                    return False
                
                # Validate expiry date
                current_year = datetime.now().year
                if details['expiry_year'] < current_year:
                    return False
                if details['expiry_year'] == current_year and details['expiry_month'] < datetime.now().month:
                    return False
            
            elif payment_method.type == PaymentMethodType.PAYPAL:
                if 'email' not in details:
                    return False
                # Basic email validation
                email = details['email']
                if '@' not in email or '.' not in email.split('@')[-1]:
                    return False
            
            elif payment_method.type == PaymentMethodType.BANK_TRANSFER:
                required_fields = ['account_number', 'routing_number', 'account_holder_name', 'bank_name']
                if not all(field in details for field in required_fields):
                    return False
                
                # Validate routing number (9 digits)
                routing = details['routing_number']
                if not routing.isdigit() or len(routing) != 9:
                    return False
            
            return True
            
        except Exception:
            return False
    
    async def generate_receipt(self, payment_id: str) -> Receipt:
        """Generate receipt for a completed payment."""
        # Get payment result
        payment_result = self._payment_storage.get(payment_id)
        if not payment_result:
            if self.repository:
                payment_result = await self.repository.get_payment_by_id(payment_id)
        
        if not payment_result:
            raise ValueError(f"Payment {payment_id} not found")
        
        if payment_result.status != PaymentStatus.COMPLETED:
            raise ValueError(f"Cannot generate receipt for payment with status {payment_result.status}")
        
        # Generate receipt
        receipt_id = str(uuid.uuid4())
        receipt_number = f"RCP-{datetime.now().strftime('%Y%m%d')}-{receipt_id[:8].upper()}"
        
        # Extract order_id from gateway response or use a default
        order_id = "unknown"
        if payment_result.gateway_response and 'order_id' in payment_result.gateway_response:
            order_id = payment_result.gateway_response['order_id']
        
        receipt = Receipt(
            id=receipt_id,
            payment_id=payment_id,
            order_id=order_id,
            amount=Decimal('0.00'),  # Will be set from payment data
            currency="USD",  # Will be set from payment data
            payment_method_type="unknown",  # Will be set from payment data
            issued_at=datetime.utcnow(),
            receipt_number=receipt_number,
            merchant_info={
                'name': 'Marketplace Platform',
                'address': '123 Commerce St, Business City, BC 12345',
                'tax_id': 'TAX123456789',
                'contact': 'support@marketplace.com'
            }
        )
        
        # Store receipt
        self._receipt_storage[payment_id] = receipt
        if self.repository:
            await self.repository.save_receipt(receipt)
        
        return receipt
    
    async def refund_payment(self, payment_id: str, amount: Decimal) -> RefundResult:
        """Process a payment refund."""
        # Get original payment
        payment_result = self._payment_storage.get(payment_id)
        if not payment_result:
            if self.repository:
                payment_result = await self.repository.get_payment_by_id(payment_id)
        
        if not payment_result:
            raise ValueError(f"Payment {payment_id} not found")
        
        if payment_result.status != PaymentStatus.COMPLETED:
            raise ValueError(f"Cannot refund payment with status {payment_result.status}")
        
        # Validate refund amount
        if amount <= 0:
            raise ValueError("Refund amount must be positive")
        
        # For simplicity, we'll allow full refunds only in this implementation
        # In a real system, you'd track partial refunds and remaining amounts
        
        try:
            # Simulate refund processing
            await asyncio.sleep(0.1)  # Simulate processing time
            
            refund_id = str(uuid.uuid4())
            
            # Simulate refund success (90% success rate)
            import random
            if random.random() < 0.9:
                refund_result = RefundResult(
                    refund_id=refund_id,
                    status="completed",
                    amount=amount,
                    message="Refund processed successfully"
                )
            else:
                refund_result = RefundResult(
                    refund_id=refund_id,
                    status="failed",
                    amount=amount,
                    message="Refund processing failed"
                )
            
            # Store refund result
            if self.repository:
                await self.repository.save_refund_result(refund_result)
            
            return refund_result
            
        except Exception as e:
            return RefundResult(
                refund_id=str(uuid.uuid4()),
                status="failed",
                amount=amount,
                message=f"Refund error: {str(e)}"
            )
    
    def encrypt_payment_method(self, payment_method: PaymentMethod) -> PaymentMethod:
        """Encrypt sensitive payment method details."""
        encrypted_details = self.encryption.encrypt_payment_details(payment_method.details)
        
        return PaymentMethod(
            type=payment_method.type,
            details={'encrypted_data': encrypted_details}
        )
    
    def get_masked_payment_details(self, payment_method: PaymentMethod) -> Dict[str, Any]:
        """Get masked payment details for safe display."""
        return self.encryption.mask_sensitive_data(payment_method.details, payment_method.type)