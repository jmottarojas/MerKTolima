"""Payment endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from pydantic import BaseModel
from decimal import Decimal

from ...services.payments.service import PaymentService, PaymentData, PaymentMethod, PaymentMethodType, PaymentResult, Receipt, RefundResult
from ...shared.models import BaseResponse
from ..dependencies import get_current_user

router = APIRouter(tags=["payments"])

# Initialize payment service
payment_service = PaymentService()


class PaymentMethodRequest(BaseModel):
    """Payment method request model."""
    type: str  # "card", "paypal", "bank_transfer"
    details: Dict[str, Any]


class PaymentRequest(BaseModel):
    """Payment request model."""
    order_id: str
    amount: Decimal
    currency: str = "USD"
    payment_method: PaymentMethodRequest
    billing_address: Optional[Dict[str, str]] = None


class RefundRequest(BaseModel):
    """Refund request model."""
    amount: Decimal


class PaymentResponse(BaseModel):
    """Payment response model."""
    payment_id: str
    status: str
    transaction_id: Optional[str] = None
    message: Optional[str] = None
    processed_at: str


class ReceiptResponse(BaseModel):
    """Receipt response model."""
    id: str
    payment_id: str
    order_id: str
    amount: Decimal
    currency: str
    payment_method_type: str
    issued_at: str
    receipt_number: str
    merchant_info: Dict[str, str]


class RefundResponse(BaseModel):
    """Refund response model."""
    refund_id: str
    status: str
    amount: Decimal
    message: Optional[str] = None
    processed_at: str


@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    request: PaymentRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process a payment."""
    try:
        # Convert payment method type string to enum
        payment_method_type = PaymentMethodType.CARD
        if request.payment_method.type == "paypal":
            payment_method_type = PaymentMethodType.PAYPAL
        elif request.payment_method.type == "bank_transfer":
            payment_method_type = PaymentMethodType.BANK_TRANSFER
        
        # Create payment method
        payment_method = PaymentMethod(
            type=payment_method_type,
            details=request.payment_method.details
        )
        
        # Encrypt payment method for security
        encrypted_payment_method = payment_service.encrypt_payment_method(payment_method)
        
        # Create payment data
        payment_data = PaymentData(
            order_id=request.order_id,
            amount=request.amount,
            currency=request.currency,
            payment_method=encrypted_payment_method,
            billing_address=request.billing_address
        )
        
        # Process payment
        result = await payment_service.process_payment(payment_data)
        
        return PaymentResponse(
            payment_id=result.payment_id,
            status=result.status.value,
            transaction_id=result.transaction_id,
            message=result.message,
            processed_at=result.processed_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment processing error: {str(e)}")


@router.post("/validate-method", response_model=BaseResponse)
async def validate_payment_method(
    request: PaymentMethodRequest,
    current_user: dict = Depends(get_current_user)
):
    """Validate a payment method."""
    try:
        # Convert payment method type string to enum
        payment_method_type = PaymentMethodType.CARD
        if request.type == "paypal":
            payment_method_type = PaymentMethodType.PAYPAL
        elif request.type == "bank_transfer":
            payment_method_type = PaymentMethodType.BANK_TRANSFER
        
        # Create payment method
        payment_method = PaymentMethod(
            type=payment_method_type,
            details=request.details
        )
        
        # Validate payment method
        is_valid = await payment_service.validate_payment_method(payment_method)
        
        if is_valid:
            return BaseResponse(
                success=True,
                message="Payment method is valid"
            )
        else:
            return BaseResponse(
                success=False,
                message="Payment method is invalid"
            )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{payment_id}/receipt", response_model=ReceiptResponse)
async def get_receipt(
    payment_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Generate and get receipt for a payment."""
    try:
        receipt = await payment_service.generate_receipt(payment_id)
        
        return ReceiptResponse(
            id=receipt.id,
            payment_id=receipt.payment_id,
            order_id=receipt.order_id,
            amount=receipt.amount,
            currency=receipt.currency,
            payment_method_type=receipt.payment_method_type,
            issued_at=receipt.issued_at.isoformat(),
            receipt_number=receipt.receipt_number,
            merchant_info=receipt.merchant_info
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/refund", response_model=RefundResponse)
async def refund_payment(
    payment_id: str,
    request: RefundRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process a refund for a payment."""
    try:
        # Note: In a real system, you'd need to verify that the user has permission
        # to refund this payment (e.g., they are the merchant or have admin rights)
        
        refund_result = await payment_service.refund_payment(payment_id, request.amount)
        
        return RefundResponse(
            refund_id=refund_result.refund_id,
            status=refund_result.status,
            amount=refund_result.amount,
            message=refund_result.message,
            processed_at=refund_result.processed_at.isoformat()
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/methods/mask", response_model=Dict[str, Any])
async def get_masked_payment_details(
    payment_method: PaymentMethodRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get masked payment details for safe display."""
    try:
        # Convert payment method type string to enum
        payment_method_type = PaymentMethodType.CARD
        if payment_method.type == "paypal":
            payment_method_type = PaymentMethodType.PAYPAL
        elif payment_method.type == "bank_transfer":
            payment_method_type = PaymentMethodType.BANK_TRANSFER
        
        # Create payment method
        payment_method_obj = PaymentMethod(
            type=payment_method_type,
            details=payment_method.details
        )
        
        # Get masked details
        masked_details = payment_service.get_masked_payment_details(payment_method_obj)
        
        return {
            "type": payment_method.type,
            "masked_details": masked_details
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))