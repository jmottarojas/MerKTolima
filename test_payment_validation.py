#!/usr/bin/env python3
"""
Test script to debug payment method validation.
"""

import asyncio
from src.services.payments.service import PaymentService, PaymentMethod, PaymentMethodType
from src.services.payments.repository import InMemoryPaymentRepository

async def test_payment_validation():
    """Test payment method validation."""
    
    print("🧪 TESTING PAYMENT METHOD VALIDATION")
    print("="*60)
    
    # Create payment service
    payment_repo = InMemoryPaymentRepository()
    payment_service = PaymentService(payment_repo)
    
    # Create test payment method
    payment_method = PaymentMethod(
        type=PaymentMethodType.CARD,
        details={
            "card_number": "4000000000000002",
            "expiry_month": 12,
            "expiry_year": 2027,
            "cvv": "123",
            "cardholder_name": "Test User"
        }
    )
    
    print(f"Payment method type: {payment_method.type}")
    print(f"Payment method details: {payment_method.details}")
    
    # Test validation
    is_valid = await payment_service.validate_payment_method(payment_method)
    print(f"Validation result: {is_valid}")
    
    if not is_valid:
        print("❌ Payment method validation failed")
        
        # Test individual validations
        details = payment_method.details
        
        # Check required fields
        required_fields = ['card_number', 'expiry_month', 'expiry_year', 'cvv', 'cardholder_name']
        missing_fields = [field for field in required_fields if field not in details]
        if missing_fields:
            print(f"   Missing fields: {missing_fields}")
        else:
            print("   ✅ All required fields present")
        
        # Check card number
        card_number = details['card_number'].replace(' ', '')
        if not card_number.isdigit():
            print(f"   ❌ Card number not digits: {card_number}")
        elif len(card_number) < 13 or len(card_number) > 19:
            print(f"   ❌ Card number length invalid: {len(card_number)}")
        else:
            print(f"   ✅ Card number valid: {card_number}")
        
        # Check expiry date
        from datetime import datetime
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        print(f"   Current date: {current_month}/{current_year}")
        print(f"   Expiry date: {details['expiry_month']}/{details['expiry_year']}")
        
        if details['expiry_year'] < current_year:
            print(f"   ❌ Expiry year in past: {details['expiry_year']} < {current_year}")
        elif details['expiry_year'] == current_year and details['expiry_month'] < current_month:
            print(f"   ❌ Expiry month in past: {details['expiry_month']} < {current_month}")
        else:
            print(f"   ✅ Expiry date valid")
    else:
        print("✅ Payment method validation passed")

if __name__ == "__main__":
    asyncio.run(test_payment_validation())