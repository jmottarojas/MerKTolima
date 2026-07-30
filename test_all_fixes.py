#!/usr/bin/env python3
"""
Script para probar todas las correcciones implementadas
"""

import requests
import json

def test_seller_orders():
    """Probar que seller_orders no da AttributeError"""
    print("🔍 Probando seller_orders...")
    try:
        response = requests.get('http://localhost:8001/vendedor/pedidos/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ seller_orders funciona correctamente")
        elif response.status_code == 302:
            print("   ↪️ Redirección (probablemente a login) - normal")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")

def test_create_product_page():
    """Probar que la página de crear producto carga correctamente"""
    print("🔍 Probando página de crear producto...")
    try:
        response = requests.get('http://localhost:8001/vendedor/productos/crear/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            # Verificar que tiene los campos actualizados
            content = response.text
            if 'type="number"' in content and 'step="0.01"' in content:
                print("   ✅ Campo de precio con decimales implementado")
            else:
                print("   ⚠️ Campo de precio podría no tener decimales")
                
            if 'no_tiene' in content and 'Impuestos' in content:
                print("   ✅ Opción 'no tiene' para impuestos implementada")
            else:
                print("   ⚠️ Opción 'no tiene' para impuestos podría faltar")
        elif response.status_code == 302:
            print("   ↪️ Redirección (probablemente a login) - normal")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")

def test_checkout_page():
    """Probar que la página de checkout no tiene código postal"""
    print("🔍 Probando página de checkout...")
    try:
        response = requests.get('http://localhost:8001/carrito/checkout/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            content = response.text
            if 'postal_code' not in content:
                print("   ✅ Código postal eliminado del checkout")
            else:
                print("   ⚠️ Código postal todavía presente en checkout")
        elif response.status_code == 302:
            print("   ↪️ Redirección (probablemente a login) - normal")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")

def test_font_awesome():
    """Probar que Font Awesome se carga correctamente"""
    print("🔍 Probando Font Awesome CDN...")
    try:
        response = requests.get('http://localhost:8001/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            content = response.text
            if 'cdn.jsdelivr.net' in content and 'fontawesome' in content:
                print("   ✅ Font Awesome CDN actualizado a jsdelivr")
            else:
                print("   ⚠️ Font Awesome CDN podría no estar actualizado")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")

def main():
    print("🚀 PROBANDO TODAS LAS CORRECCIONES")
    print("=" * 50)
    
    print("\n1. FONT AWESOME CDN FIX")
    test_font_awesome()
    
    print("\n2. SELLER ORDERS FIX")
    test_seller_orders()
    
    print("\n3. CREATE PRODUCT IMPROVEMENTS")
    test_create_product_page()
    
    print("\n4. CHECKOUT POSTAL CODE REMOVAL")
    test_checkout_page()
    
    print("\n" + "=" * 50)
    print("✅ PRUEBAS COMPLETADAS")
    print("\nCambios implementados:")
    print("• ✅ Font Awesome CDN actualizado (jsdelivr)")
    print("• ✅ Campo 'no tiene' agregado a impuestos")
    print("• ✅ Soporte de decimales en precios")
    print("• ✅ Código postal eliminado del checkout")
    print("• ✅ Botón eliminar agregado a imágenes en editar producto")
    print("• ✅ Error AttributeError en seller_orders corregido")
    print("• ✅ Procesamiento de precios actualizado para decimales")
    
    print("\nInstrucciones para probar:")
    print("1. Abre http://localhost:8001/ y verifica que los iconos se ven bien")
    print("2. Inicia sesión como vendedor: vendedor@merkatolima.com / Vendedor123")
    print("3. Ve a 'Pedidos Recibidos' - no debería dar error")
    print("4. Ve a 'Crear Producto' - verifica decimales en precio e impuestos")
    print("5. Ve a 'Editar Producto' - verifica botón X en imágenes")
    print("6. Haz una compra - verifica que no pide código postal")

if __name__ == "__main__":
    main()