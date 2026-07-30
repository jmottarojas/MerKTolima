#!/usr/bin/env python3
"""
Script para actualizar los precios de productos de USD a COP
Tasa de cambio aproximada: 1 USD = 4,000 COP (ajustar según tasa actual)
"""

import requests
import json

# Configuración
API_BASE_URL = "http://localhost:8000"
EXCHANGE_RATE = 4000  # 1 USD = 4000 COP (ajustar según tasa actual)

def get_all_products():
    """Obtener todos los productos de la API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/products/")
        response.raise_for_status()
        return response.json().get('products', [])
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener productos: {e}")
        return []

def update_product_price(product_id, new_price):
    """Actualizar el precio de un producto"""
    try:
        # Primero obtener el producto actual
        response = requests.get(f"{API_BASE_URL}/api/v1/products/{product_id}")
        response.raise_for_status()
        product = response.json()
        
        # Actualizar solo el precio y la moneda
        product_data = {
            'name': product['name'],
            'description': product['description'],
            'price': new_price,
            'currency': 'COP',
            'category': product['category'],
            'images': product.get('images', []),
            'inventory': product.get('inventory', {})
        }
        
        # Enviar actualización
        response = requests.put(
            f"{API_BASE_URL}/api/v1/products/{product_id}",
            json=product_data,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error al actualizar producto {product_id}: {e}")
        return False

def main():
    """Función principal"""
    print("🔄 Iniciando actualización de moneda USD a COP...")
    print(f"💱 Tasa de cambio utilizada: 1 USD = {EXCHANGE_RATE:,} COP")
    
    # Obtener todos los productos
    products = get_all_products()
    if not products:
        print("❌ No se pudieron obtener los productos")
        return
    
    print(f"📦 Se encontraron {len(products)} productos")
    
    updated_count = 0
    error_count = 0
    
    for product in products:
        product_id = product.get('id')
        current_price = product.get('price', 0)
        current_currency = product.get('currency', 'USD')
        
        # Solo actualizar si la moneda es USD
        if current_currency == 'USD':
            new_price = int(current_price * EXCHANGE_RATE)
            print(f"🔄 Actualizando {product['name']}: ${current_price} USD → ${new_price:,} COP")
            
            if update_product_price(product_id, new_price):
                updated_count += 1
                print(f"✅ Producto {product['name']} actualizado exitosamente")
            else:
                error_count += 1
                print(f"❌ Error al actualizar {product['name']}")
        else:
            print(f"⏭️  Saltando {product['name']} (ya está en {current_currency})")
    
    print(f"\n📊 Resumen:")
    print(f"✅ Productos actualizados: {updated_count}")
    print(f"❌ Errores: {error_count}")
    print(f"📦 Total procesados: {len(products)}")
    
    if updated_count > 0:
        print(f"\n🎉 ¡Actualización completada! Los precios ahora están en pesos colombianos.")
    else:
        print(f"\n💡 No se actualizaron productos. Todos ya estaban en COP o no había productos.")

if __name__ == "__main__":
    main()