"""Payment repository interface."""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc

from .service import PaymentResult, Receipt, RefundResult
from ...shared.db_models import PaymentDB, ReceiptDB, RefundDB
from ...shared.models import PaymentStatus


class PaymentRepository(ABC):
    """Abstract payment repository interface."""
    
    @abstractmethod
    async def save_payment_result(self, payment_result: PaymentResult) -> None:
        """Save payment result."""
        pass
    
    @abstractmethod
    async def get_payment_by_id(self, payment_id: str) -> Optional[PaymentResult]:
        """Get payment by ID."""
        pass
    
    @abstractmethod
    async def get_payments_by_order(self, order_id: str) -> List[PaymentResult]:
        """Get payments by order ID."""
        pass
    
    @abstractmethod
    async def save_receipt(self, receipt: Receipt) -> None:
        """Save receipt."""
        pass
    
    @abstractmethod
    async def get_receipt_by_payment(self, payment_id: str) -> Optional[Receipt]:
        """Get receipt by payment ID."""
        pass
    
    @abstractmethod
    async def save_refund_result(self, refund_result: RefundResult) -> None:
        """Save refund result."""
        pass
    
    @abstractmethod
    async def get_refunds_by_payment(self, payment_id: str) -> List[RefundResult]:
        """Get refunds by payment ID."""
        pass


class SQLAlchemyPaymentRepository(PaymentRepository):
    """SQLAlchemy implementation of payment repository."""
    
    def __init__(self, db_session: Session):
        """Initialize with database session."""
        self.db = db_session
    
    def _db_payment_to_pydantic(self, db_payment: PaymentDB) -> PaymentResult:
        """Convert SQLAlchemy payment model to Pydantic model."""
        from .service import PaymentStatus as ServicePaymentStatus
        
        # Map database status to service status
        if db_payment.payment_status == PaymentStatus.COMPLETED:
            status = ServicePaymentStatus.COMPLETED
        elif db_payment.payment_status == PaymentStatus.FAILED:
            status = ServicePaymentStatus.FAILED
        elif db_payment.payment_status == PaymentStatus.PENDING:
            status = ServicePaymentStatus.PENDING
        else:
            status = ServicePaymentStatus.FAILED
        
        return PaymentResult(
            payment_id=db_payment.id,
            status=status,
            transaction_id=db_payment.transaction_id,
            message="Payment processed successfully" if db_payment.payment_status == PaymentStatus.COMPLETED else "Payment failed",
            gateway_response=db_payment.processor_response or {}
        )
    
    def _db_receipt_to_pydantic(self, db_receipt: ReceiptDB) -> Receipt:
        """Convert SQLAlchemy receipt model to Pydantic model."""
        # Extract amount and currency from receipt data if available
        receipt_data = db_receipt.receipt_data or {}
        amount = Decimal(receipt_data.get('total', '0.00'))
        currency = receipt_data.get('currency', 'USD')
        
        return Receipt(
            id=db_receipt.id,
            payment_id=db_receipt.payment_id,
            order_id=receipt_data.get('order_id', 'unknown'),
            amount=amount,
            currency=currency,
            payment_method_type=receipt_data.get('payment_method_type', 'unknown'),
            issued_at=db_receipt.created_at,
            receipt_number=db_receipt.receipt_number,
            merchant_info=receipt_data.get('merchant_info', {})
        )
    
    def _db_refund_to_pydantic(self, db_refund: RefundDB) -> RefundResult:
        """Convert SQLAlchemy refund model to Pydantic model."""
        return RefundResult(
            refund_id=db_refund.id,
            payment_id=db_refund.payment_id,
            success=db_refund.status == "completed",
            refund_amount=db_refund.refund_amount,
            transaction_id=db_refund.transaction_id,
            processor_response=db_refund.processor_response or {},
            error_message=None if db_refund.status == "completed" else "Refund failed",
            created_at=db_refund.created_at
        )
    
    async def save_payment_result(self, payment_result: PaymentResult) -> None:
        """Save payment result."""
        from .service import PaymentStatus as ServicePaymentStatus
        
        # Map service status to database status
        if payment_result.status == ServicePaymentStatus.COMPLETED:
            db_status = PaymentStatus.COMPLETED
        elif payment_result.status == ServicePaymentStatus.FAILED:
            db_status = PaymentStatus.FAILED
        elif payment_result.status == ServicePaymentStatus.PENDING:
            db_status = PaymentStatus.PENDING
        else:
            db_status = PaymentStatus.FAILED
        
        # Check if payment already exists
        existing_payment = self.db.query(PaymentDB).filter(PaymentDB.id == payment_result.payment_id).first()
        
        if existing_payment:
            # Update existing payment
            existing_payment.payment_status = db_status
            existing_payment.transaction_id = payment_result.transaction_id
            existing_payment.processor_response = payment_result.gateway_response
            existing_payment.payment_date = datetime.utcnow() if payment_result.status == ServicePaymentStatus.COMPLETED else None
            existing_payment.updated_at = datetime.utcnow()
        else:
            # Create new payment - we need to extract order_id and other fields from gateway_response
            order_id = payment_result.gateway_response.get('order_id', 'unknown') if payment_result.gateway_response else 'unknown'
            amount = Decimal(payment_result.gateway_response.get('amount', '0.00')) if payment_result.gateway_response else Decimal('0.00')
            currency = payment_result.gateway_response.get('currency', 'USD') if payment_result.gateway_response else 'USD'
            payment_method = payment_result.gateway_response.get('payment_method', 'unknown') if payment_result.gateway_response else 'unknown'
            
            db_payment = PaymentDB(
                id=payment_result.payment_id,
                order_id=order_id,
                payment_method=payment_method,
                payment_status=db_status,
                transaction_id=payment_result.transaction_id,
                amount=amount,
                currency=currency,
                processor_response=payment_result.gateway_response,
                payment_date=datetime.utcnow() if payment_result.status == ServicePaymentStatus.COMPLETED else None,
                created_at=payment_result.processed_at,
                updated_at=datetime.utcnow()
            )
            self.db.add(db_payment)
        
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
    
    async def get_payment_by_id(self, payment_id: str) -> Optional[PaymentResult]:
        """Get payment by ID."""
        db_payment = self.db.query(PaymentDB).filter(PaymentDB.id == payment_id).first()
        if db_payment:
            return self._db_payment_to_pydantic(db_payment)
        return None
    
    async def get_payments_by_order(self, order_id: str) -> List[PaymentResult]:
        """Get payments by order ID."""
        db_payments = self.db.query(PaymentDB).filter(PaymentDB.order_id == order_id).order_by(desc(PaymentDB.created_at)).all()
        return [self._db_payment_to_pydantic(db_payment) for db_payment in db_payments]
    
    async def save_receipt(self, receipt: Receipt) -> None:
        """Save receipt."""
        # Create receipt data with all the receipt information
        receipt_data = {
            'order_id': receipt.order_id,
            'total': str(receipt.amount),
            'currency': receipt.currency,
            'payment_method_type': receipt.payment_method_type,
            'merchant_info': receipt.merchant_info
        }
        
        db_receipt = ReceiptDB(
            id=receipt.id,
            payment_id=receipt.payment_id,
            receipt_number=receipt.receipt_number,
            receipt_data=receipt_data,
            created_at=receipt.issued_at
        )
        
        try:
            self.db.add(db_receipt)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
    
    async def get_receipt_by_payment(self, payment_id: str) -> Optional[Receipt]:
        """Get receipt by payment ID."""
        db_receipt = self.db.query(ReceiptDB).filter(ReceiptDB.payment_id == payment_id).first()
        if db_receipt:
            return self._db_receipt_to_pydantic(db_receipt)
        return None
    
    async def save_refund_result(self, refund_result: RefundResult) -> None:
        """Save refund result."""
        db_refund = RefundDB(
            id=refund_result.refund_id,
            payment_id=refund_result.payment_id,
            refund_amount=refund_result.refund_amount,
            reason="Refund requested",
            status="completed" if refund_result.success else "failed",
            transaction_id=refund_result.transaction_id,
            processor_response=refund_result.processor_response,
            refund_date=datetime.utcnow() if refund_result.success else None,
            created_at=refund_result.created_at,
            updated_at=datetime.utcnow()
        )
        
        try:
            self.db.add(db_refund)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
    
    async def get_refunds_by_payment(self, payment_id: str) -> List[RefundResult]:
        """Get refunds by payment ID."""
        db_refunds = self.db.query(RefundDB).filter(RefundDB.payment_id == payment_id).order_by(desc(RefundDB.created_at)).all()
        return [self._db_refund_to_pydantic(db_refund) for db_refund in db_refunds]


class InMemoryPaymentRepository(PaymentRepository):
    """In-memory implementation of payment repository for testing."""
    
    def __init__(self):
        """Initialize repository."""
        self._payments: Dict[str, PaymentResult] = {}
        self._receipts: Dict[str, Receipt] = {}
        self._refunds: Dict[str, List[RefundResult]] = {}
    
    async def save_payment_result(self, payment_result: PaymentResult) -> None:
        """Save payment result."""
        self._payments[payment_result.payment_id] = payment_result
    
    async def get_payment_by_id(self, payment_id: str) -> Optional[PaymentResult]:
        """Get payment by ID."""
        return self._payments.get(payment_id)
    
    async def get_payments_by_order(self, order_id: str) -> List[PaymentResult]:
        """Get payments by order ID."""
        return [payment for payment in self._payments.values() if payment.order_id == order_id]
    
    async def save_receipt(self, receipt: Receipt) -> None:
        """Save receipt."""
        self._receipts[receipt.payment_id] = receipt
    
    async def get_receipt_by_payment(self, payment_id: str) -> Optional[Receipt]:
        """Get receipt by payment ID."""
        return self._receipts.get(payment_id)
    
    async def save_refund_result(self, refund_result: RefundResult) -> None:
        """Save refund result."""
        if refund_result.payment_id not in self._refunds:
            self._refunds[refund_result.payment_id] = []
        self._refunds[refund_result.payment_id].append(refund_result)
    
    async def get_refunds_by_payment(self, payment_id: str) -> List[RefundResult]:
        """Get refunds by payment ID."""
        return self._refunds.get(payment_id, [])