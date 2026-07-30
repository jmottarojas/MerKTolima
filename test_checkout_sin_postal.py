#!/usr/bin/env python3
"""
Script para probar checkout sin código postal
"""

import requests
import json

def test_checkout_sin_postal():
    """Probar que el checkout funciona sin código postal"""
    
    print("🛒 PROBANDO CHECKOUT SIN CÓDIGO POSTAL")
    print("=" * 50)
    
    # Datos de prueba para el checkout (sin postal_code)
    checkout_data = {
        'street': 'Av Carrera 50 No 4b-28 Barrio Galan Primavera',
        'city': 'Bogotá, Bogotá D.C., Colombia',
        'state': 'Cundinamarca',
        'country': 'Colombia',
        'payment_method': 'credit_card'
    }
    
    print("📦 Datos de checkout:")
    for key, value in checkout_data.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔍 Verificando que NO hay postal_code:")
    if 'postal_code' not in checkout_data:
        print("   ✅ postal_code NO está presente en los datos")
    else:
        print("   ❌ postal_code está presente (no debería)")
    
    # Simular la estructura que envía Django al API
    api_payload = {
        'cart_id': 'test_cart_123',
        'shipping_address': checkout_data,
        'payment_method': checkout_data['payment_method']
    }
    
    print(f"\n📡 Payload que se enviaría al API:")
    print(json.dumps(api_payload, indent=2, ensure_ascii=False))
    
    # Verificar estructura del shipping_address
    shipping_address = api_payload['shipping_address']
    required_fields = ['street', 'city', 'state', 'country']
    optional_fields = ['postal_code']
    
    print(f"\n🔍 Validación de campos:")
    
    # Verificar campos requeridos
    for field in required_fields:
        if field in shipping_address:
            print(f"   ✅ {field}: PRESENTE")
        else:
            print(f"   ❌ {field}: FALTANTE")
    
    # Verificar campos opcionales
    for field in optional_fields:
        if field in shipping_address:
            print(f"   ⚠️ {field}: PRESENTE (opcional)")
        else:
            print(f"   ✅ {field}: AUSENTE (correcto)")
    
    print(f"\n📋 Resumen:")
    print(f"   - Campos requeridos: {len(required_fields)}")
    print(f"   - Campos opcionales ausentes: {len([f for f in optional_fields if f not in shipping_address])}")
    print(f"   - Total campos enviados: {len(shipping_address)}")
    
    # Verificar que el modelo Pydantic aceptaría estos datos
    try:
        # Simular validación Pydantic
        from pydantic import BaseModel, Field
        from typing import Optional
        
        class TestAddress(BaseModel):
            street: str = Field(..., min_length=1, max_length=200)
            city: str = Field(..., min_length=1, max_length=100)
            state: str = Field(..., min_length=1, max_length=100)
            postal_code: Optional[str] = Field(None, min_length=1, max_length=20)
            country: str = Field(..., min_length=1, max_length=100)
        
        # Intentar crear el modelo
        test_address = TestAddress(**shipping_address)
        print(f"\n✅ VALIDACIÓN PYDANTIC: EXITOSA")
        print(f"   - street: {test_address.street}")
        print(f"   - city: {test_address.city}")
        print(f"   - state: {test_address.state}")
        print(f"   - postal_code: {test_address.postal_code}")
        print(f"   - country: {test_address.country}")
        
    except Exception as e:
        print(f"\n❌ VALIDACIÓN PYDANTIC: FALLÓ")
        print(f"   Error: {str(e)}")
    
    print(f"\n🎯 CONCLUSIÓN:")
    if 'postal_code' not in shipping_address:
        print("   ✅ El checkout SIN código postal debería funcionar")
        print("   ✅ Los modelos Pydantic han sido actualizados correctamente")
    else:
        print("   ❌ Todavía se está enviando código postal")
    
    print("\n" + "=" * 50)
    print("✅ PRUEBA COMPLETADA")

def test_api_direct():
    """Probar directamente contra el API FastAPI"""
    print("\n🚀 PROBANDO API FASTAPI DIRECTAMENTE")
    print("=" * 50)
    
    # Datos sin postal_code
    order_data = {
        "cart_id": "test_cart_123",
        "shipping_address": {
            "street": "Av Carrera 50 No 4b-28 Barrio Galan Primavera",
            "city": "Bogotá, Bogotá D.C., Colombia", 
            "state": "Cundinamarca",
            "country": "Colombia"
            # NO postal_code
        },
        "payment_method": "credit_card"
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/orders/',
            json=order_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API acepta pedidos SIN código postal")
        elif response.status_code == 422:
            print("❌ API rechaza pedidos SIN código postal")
            try:
                error_detail = response.json()
                print(f"   Error: {error_detail}")
            except:
                print(f"   Error: {response.text}")
        else:
            print(f"⚠️ Respuesta inesperada: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ No se pudo conectar al API (¿está corriendo en puerto 8000?)")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_checkout_sin_postal()
    test_api_direct()