"""Script para corregir el status de productos con inventario."""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.products.service import ProductService


async def fix_product_status():
    """Corregir el status de todos los productos basado en su inventario."""
    product_service = ProductService()
    
    print("\n" + "="*60)
    print("🔧 CORRIGIENDO STATUS DE PRODUCTOS")
    print("="*60 + "\n")
    
    # Obtener todos los productos
    all_products = list(product_service._products.values())
    
    if not all_products:
        print("⚠️  No hay productos en el sistema")
        return
    
    print(f"📦 Total de productos encontrados: {len(all_products)}\n")
    
    fixed_count = 0
    
    for product in all_products:
        old_status = product.status
        correct_status = "active" if product.inventory_quantity > 0 else "out_of_stock"
        
        if old_status != correct_status:
            print(f"🔄 Producto: {product.name}")
            print(f"   - ID: {product.id}")
            print(f"   - Inventario: {product.inventory_quantity}")
            print(f"   - Status anterior: {old_status}")
            print(f"   - Status correcto: {correct_status}")
            
            # Actualizar el status directamente
            product.status = correct_status
            product_service._products[product.id] = product
            
            fixed_count += 1
            print(f"   ✅ Corregido\n")
        else:
            print(f"✓ Producto OK: {product.name} (status: {old_status}, inventario: {product.inventory_quantity})")
    
    print("\n" + "="*60)
    print(f"✅ PROCESO COMPLETADO")
    print(f"   - Productos revisados: {len(all_products)}")
    print(f"   - Productos corregidos: {fixed_count}")
    print("="*60 + "\n")
    
    # Mostrar resumen de productos disponibles
    available_products = [p for p in all_products if p.status == "active" and p.inventory_quantity > 0]
    
    if available_products:
        print("\n📋 PRODUCTOS DISPONIBLES PARA COMPRA:\n")
        for product in available_products:
            print(f"   ✅ {product.name}")
            print(f"      - ID: {product.id}")
            print(f"      - Precio: ${product.price} {product.currency}")
            print(f"      - Stock: {product.inventory_quantity} unidades")
            print(f"      - Categoría: {product.category}")
            print()


if __name__ == "__main__":
    asyncio.run(fix_product_status())
