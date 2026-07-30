from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import json
import uuid
import os
from decimal import Decimal
from .api_client import api_client


def home(request):
    """Página de inicio."""
    # Obtener productos destacados
    products_response = api_client.get_products(page=1, page_size=8)
    featured_products = products_response.get('products', []) if isinstance(products_response, dict) and 'error' not in products_response else []
    
    context = {
        'featured_products': featured_products,
    }
    return render(request, 'marketplace/home.html', context)


def products(request):
    """Lista de productos."""
    page = int(request.GET.get('page', 1))
    category = request.GET.get('category')
    
    if category:
        products_response = api_client.search_products(category=category, page=page, page_size=12)
    else:
        products_response = api_client.get_products(page=page, page_size=12)
    
    products_list = products_response.get('products', []) if 'error' not in products_response else []
    total_count = products_response.get('total_count', 0)
    
    # Obtener categorías únicas
    categories = ['Electrónicos', 'Ropa', 'Hogar', 'Deportes', 'Libros', 'Juguetes', 'Belleza', 'Automóviles', 'Motocicletas']
    
    context = {
        'products': products_list,
        'categories': categories,
        'current_category': category,
        'total_count': total_count,
        'current_page': page,
    }
    return render(request, 'marketplace/products.html', context)


def product_detail(request, product_id):
    """Detalle de producto."""
    product_response = api_client.get_product(product_id)
    
    if 'error' in product_response:
        messages.error(request, 'Producto no encontrado.')
        return redirect('marketplace:products')
    
    product = product_response
    
    # Obtener productos relacionados (misma categoría)
    related_response = api_client.search_products(category=product.get('category'), page_size=4)
    related_products = related_response.get('products', []) if 'error' not in related_response else []
    # Filtrar el producto actual
    related_products = [p for p in related_products if p.get('id') != product_id][:3]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'marketplace/product_detail.html', context)


def search(request):
    """Búsqueda de productos."""
    query = request.GET.get('q', '')
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    page = int(request.GET.get('page', 1))
    
    # Convertir precios a float si existen
    try:
        min_price = float(min_price) if min_price else None
        max_price = float(max_price) if max_price else None
    except (ValueError, TypeError):
        min_price = max_price = None
    
    search_response = api_client.search_products(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
        page=page,
        page_size=12
    )
    
    products_list = search_response.get('products', []) if 'error' not in search_response else []
    total_count = search_response.get('total_count', 0)
    
    categories = ['Electrónicos', 'Ropa', 'Hogar', 'Deportes', 'Libros', 'Juguetes', 'Belleza', 'Automóviles', 'Motocicletas']
    
    context = {
        'products': products_list,
        'categories': categories,
        'query': query,
        'current_category': category,
        'min_price': min_price,
        'max_price': max_price,
        'total_count': total_count,
        'current_page': page,
    }
    return render(request, 'marketplace/search.html', context)


def register(request):
    """Registro de usuario."""
    if request.method == 'POST':
        # Obtener datos del formulario
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role', 'buyer')
        
        # Validaciones básicas
        if not all([email, password, first_name, last_name]):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'marketplace/register.html')
        
        # Registrar usuario en la API
        user_data = {
            'email': email,
            'password': password,
            'role': role,
            'first_name': first_name,
            'last_name': last_name
        }
        
        response = api_client.register_user(user_data)
        
        if 'error' in response:
            messages.error(request, f'Error al registrar usuario: {response["error"]}')
            return render(request, 'marketplace/register.html')
        
        messages.success(request, 'Usuario registrado exitosamente. Puedes iniciar sesión.')
        return redirect('marketplace:login')
    
    return render(request, 'marketplace/register.html')


def login_view(request):
    """Inicio de sesión."""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'Email y contraseña son obligatorios.')
            return render(request, 'marketplace/login.html')
        
        # Autenticar con la API
        response = api_client.login_user(email, password)
        
        if 'error' in response:
            messages.error(request, 'Credenciales inválidas.')
            return render(request, 'marketplace/login.html')
        
        # Configurar token en el cliente API
        api_client.set_auth_token(response.get('access_token'))
        
        # Obtener información del usuario usando el token
        profile_response = api_client.get_user_profile('profile', token=response.get('access_token'))  # Usar endpoint /profile
        
        if 'error' not in profile_response:
            # Guardar información del usuario en la sesión
            request.session['user_token'] = response.get('access_token')
            request.session['user_id'] = profile_response.get('id')
            request.session['user_email'] = profile_response.get('email')
            request.session['user_role'] = profile_response.get('role')
            request.session['user_first_name'] = profile_response.get('first_name')
            
            messages.success(request, f'Bienvenido, {profile_response.get("first_name", email)}!')
            
            # Redirigir según el rol del usuario
            user_role = profile_response.get('role')
            if user_role == 'seller':
                return redirect('marketplace:seller_dashboard')
            else:  # buyer
                return redirect('marketplace:home')
        else:
            messages.error(request, 'Error al obtener información del usuario.')
            return render(request, 'marketplace/login.html')
    
    return render(request, 'marketplace/login.html')


def logout_view(request):
    """Cerrar sesión."""
    # Limpiar sesión
    request.session.flush()
    api_client.clear_auth_token()
    
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('marketplace:home')


def profile(request):
    """Perfil de usuario."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para acceder a tu perfil.')
        return redirect('marketplace:login')
    
    user_id = request.session.get('user_id')
    
    if request.method == 'POST':
        # Actualizar perfil
        profile_data = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'phone': request.POST.get('phone'),
        }
        
        response = api_client.update_user_profile(user_id, profile_data, token=request.session.get('user_token'))
        
        if 'error' not in response:
            messages.success(request, 'Perfil actualizado exitosamente.')
        else:
            messages.error(request, 'Error al actualizar perfil.')
    
    # Obtener datos del perfil usando el endpoint de perfil actual
    user_token = request.session.get('user_token')
    profile_response = api_client.get_user_profile('profile', token=user_token)
    user_profile = profile_response if 'error' not in profile_response else {}
    
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'marketplace/profile.html', context)


def cart(request):
    """Carrito de compras."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para ver tu carrito.')
        return redirect('marketplace:login')
    
    user_id = request.session.get('user_id')
    user_token = request.session.get('user_token')
    if user_token:
        api_client.set_auth_token(user_token)
    cart_response = api_client.get_cart(user_id, token=user_token)
    
    cart_data = cart_response if 'error' not in cart_response else {'items': [], 'total_amount': 0}
    
    context = {
        'cart': cart_data,
    }
    return render(request, 'marketplace/cart.html', context)


def add_to_cart(request, product_id):
    """Agregar producto al carrito."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para agregar productos al carrito.')
        return redirect('marketplace:login')
    
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        user_token = request.session.get('user_token')
        if user_token:
            api_client.set_auth_token(user_token)
        quantity = int(request.POST.get('quantity', 1))
        
        response = api_client.add_to_cart(user_id, product_id, quantity)
        
        if 'error' not in response:
            messages.success(request, 'Producto agregado al carrito.')
        else:
            messages.error(request, 'Error al agregar producto al carrito.')
    
    return redirect('marketplace:product_detail', product_id=product_id)


def update_cart(request):
    """Actualizar carrito."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para actualizar el carrito.')
        return redirect('marketplace:login')
    
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        user_token = request.session.get('user_token')
        if user_token:
            api_client.set_auth_token(user_token)
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0:
            response = api_client.update_cart_item(user_id, product_id, quantity)
        else:
            response = api_client.remove_from_cart(user_id, product_id)
        
        if 'error' not in response:
            messages.success(request, 'Carrito actualizado.')
        else:
            messages.error(request, 'Error al actualizar carrito.')
    
    return redirect('marketplace:cart')


def remove_from_cart(request, product_id):
    """Eliminar producto del carrito."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para eliminar productos del carrito.')
        return redirect('marketplace:login')
    
    user_id = request.session.get('user_id')
    user_token = request.session.get('user_token')
    if user_token:
        api_client.set_auth_token(user_token)
    
    response = api_client.remove_from_cart(user_id, product_id)
    
    if 'error' not in response:
        messages.success(request, 'Producto eliminado del carrito.')
    else:
        messages.error(request, 'Error al eliminar producto.')
    
    return redirect('marketplace:cart')


def checkout(request):
    """Proceso de checkout."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para realizar el checkout.')
        return redirect('marketplace:login')
    
    user_id = request.session.get('user_id')
    
    if request.method == 'POST':
        # Procesar pedido
        # Obtener carrito primero para conseguir el cart_id
        user_token = request.session.get('user_token')
        if user_token:
            api_client.set_auth_token(user_token)
        cart_response = api_client.get_cart(user_id, token=user_token)
        cart_data = cart_response if 'error' not in cart_response else {'items': [], 'total_amount': 0}
        
        cart_id = cart_data.get('id')
        if not cart_id:
            messages.error(request, 'No se encontró el carrito. Agrega productos antes de continuar.')
            return render(request, 'marketplace/checkout.html', {'cart': cart_data})
        
        order_data = {
            'cart_id': cart_id,
            'shipping_address': {
                'street': request.POST.get('street'),
                'city': request.POST.get('city'),
                'state': request.POST.get('state'),
                'postal_code': request.POST.get('postal_code', '000000'),
                'country': 'Colombia'
            },
            'payment_method': request.POST.get('payment_method', 'credit_card')
        }
        
        # Crear pedido
        order_response = api_client.create_order(order_data, token=user_token)
        
        if 'error' not in order_response:
            # Procesar pago
            payment_data = {
                'order_id': order_response.get('id'),
                'payment_method': request.POST.get('payment_method'),
                'card_number': request.POST.get('card_number'),
                'card_holder': request.POST.get('card_holder'),
                'expiry_date': request.POST.get('expiry_date'),
                'cvv': request.POST.get('cvv')
            }
            
            payment_response = api_client.process_payment(payment_data)
            
            if 'error' not in payment_response:
                messages.success(request, 'Pedido realizado exitosamente.')
                return redirect('marketplace:order_detail', order_id=order_response.get('id'))
            else:
                messages.error(request, 'Error al procesar el pago.')
        else:
            messages.error(request, 'Error al crear el pedido.')
    
    # Obtener carrito
    user_token = request.session.get('user_token')
    if user_token:
        api_client.set_auth_token(user_token)
    cart_response = api_client.get_cart(user_id, token=user_token)
    cart_data = cart_response if 'error' not in cart_response else {'items': [], 'total_amount': 0}
    
    context = {
        'cart': cart_data,
    }
    return render(request, 'marketplace/checkout.html', context)


def orders(request):
    """Lista de pedidos del usuario."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para ver tus pedidos.')
        return redirect('marketplace:login')
    
    user_id = request.session.get('user_id')
    orders_response = api_client.get_orders_by_buyer(user_id)
    
    if isinstance(orders_response, list):
        orders_list = orders_response
    elif isinstance(orders_response, dict) and 'error' not in orders_response:
        orders_list = orders_response.get('orders', [])
    else:
        orders_list = []
    
    context = {
        'orders': orders_list,
    }
    return render(request, 'marketplace/orders.html', context)


def order_detail(request, order_id):
    """Detalle de pedido."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para ver los detalles del pedido.')
        return redirect('marketplace:login')
    
    order_response = api_client.get_order(order_id)
    
    if 'error' in order_response:
        messages.error(request, 'Pedido no encontrado.')
        return redirect('marketplace:orders')
    
    context = {
        'order': order_response,
    }
    return render(request, 'marketplace/order_detail.html', context)


def seller_dashboard(request):
    """Panel del vendedor."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para acceder al panel de vendedor.')
        return redirect('marketplace:login')
    
    user_id = request.session.get('user_id')
    user_token = request.session.get('user_token')
    
    # Configurar token para las peticiones API
    if user_token:
        api_client.set_auth_token(user_token)
    
    # Obtener productos del vendedor
    products_response = api_client.get_products_by_seller(user_id, token=user_token)
    # La API devuelve una lista directamente, no un diccionario con 'products'
    if 'error' not in products_response:
        products_list = products_response if isinstance(products_response, list) else []
    else:
        products_list = []
    
    # Obtener pedidos del vendedor
    orders_response = api_client.get_orders_by_seller(user_id)
    if isinstance(orders_response, list):
        orders_list = orders_response
    elif isinstance(orders_response, dict) and 'error' not in orders_response:
        orders_list = orders_response.get('orders', [])
    else:
        orders_list = []
    
    context = {
        'products': products_list,
        'orders': orders_list,
        'products_count': len(products_list),
        'orders_count': len(orders_list),
    }
    return render(request, 'marketplace/seller_dashboard.html', context)


def seller_products(request):
    """Productos del vendedor."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para ver tus productos.')
        return redirect('marketplace:login')
    
    user_id = request.session.get('user_id')
    user_token = request.session.get('user_token')
    
    # Configurar token para las peticiones API
    if user_token:
        api_client.set_auth_token(user_token)
    
    products_response = api_client.get_products_by_seller(user_id, token=user_token)
    
    # La API devuelve una lista directamente, no un diccionario con 'products'
    if 'error' not in products_response:
        products_list = products_response if isinstance(products_response, list) else []
    else:
        products_list = []
    
    context = {
        'products': products_list,
    }
    return render(request, 'marketplace/seller_products.html', context)


def create_product(request):
    """Crear nuevo producto."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para crear productos.')
        return redirect('marketplace:login')
    
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        user_token = request.session.get('user_token')
        
        # Configurar token para las peticiones API
        if user_token:
            api_client.set_auth_token(user_token)
        
        # Manejar imágenes - el formulario envía URLs ya subidas via /api/upload-images/
        image_urls = []
        all_image_urls = request.POST.get('all_image_urls', '')
        if all_image_urls:
            image_urls = [u.strip() for u in all_image_urls.split(',') if u.strip()]
        
        # Fallback: URL directa
        if not image_urls:
            url_image_urls = request.POST.get('url_image_urls', '')
            if url_image_urls:
                image_urls = [u.strip() for u in url_image_urls.split(',') if u.strip()]
        
        product_data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'price': float(request.POST.get('price')),
            'currency': 'COP',
            'category': request.POST.get('category'),
            'inventory_quantity': int(request.POST.get('quantity', 0)),
            'low_stock_threshold': int(request.POST.get('low_stock_threshold', 10))
        }
        
        # Agregar imágenes si existen
        if image_urls:
            product_data['images'] = image_urls
        
        response = api_client.create_product(product_data, token=user_token)
        
        if 'error' not in response:
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('marketplace:seller_products')
        else:
            messages.error(request, f'Error al crear producto: {response["error"]}')
    
    categories = ['Electrónicos', 'Ropa', 'Hogar', 'Deportes', 'Libros', 'Juguetes', 'Belleza', 'Automóviles', 'Motocicletas']
    
    context = {
        'categories': categories,
    }
    return render(request, 'marketplace/create_product.html', context)


def edit_product(request, product_id):
    """Editar producto."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para editar productos.')
        return redirect('marketplace:login')
    
    user_token = request.session.get('user_token')
    
    # Configurar token para las peticiones API
    if user_token:
        api_client.set_auth_token(user_token)
    
    # Obtener producto actual
    product_response = api_client.get_product(product_id)
    
    if 'error' in product_response:
        messages.error(request, 'Producto no encontrado.')
        return redirect('marketplace:seller_products')
    
    product = product_response
    
    if request.method == 'POST':
        # Manejar imagen
        image_urls = product.get('images', [])  # Mantener imágenes actuales por defecto
        image_option = request.POST.get('image_option', 'keep')
        
        if image_option == 'upload' and 'image_file' in request.FILES:
            # Subir nuevo archivo
            image_file = request.FILES['image_file']
            
            # Validar tipo de archivo
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
            if image_file.content_type not in allowed_types:
                messages.error(request, 'Tipo de archivo no válido. Solo se permiten JPG, PNG y GIF.')
                return render(request, 'marketplace/edit_product.html', {'product': product, 'categories': ['Electrónicos', 'Ropa', 'Hogar', 'Deportes', 'Libros', 'Juguetes', 'Belleza', 'Automóviles', 'Motocicletas']})
            
            # Validar tamaño (5MB máximo)
            if image_file.size > 5 * 1024 * 1024:
                messages.error(request, 'El archivo es demasiado grande. El tamaño máximo es 5MB.')
                return render(request, 'marketplace/edit_product.html', {'product': product, 'categories': ['Electrónicos', 'Ropa', 'Hogar', 'Deportes', 'Libros', 'Juguetes', 'Belleza', 'Automóviles', 'Motocicletas']})
            
            # Generar nombre único para el archivo
            file_extension = os.path.splitext(image_file.name)[1]
            unique_filename = f"product_{uuid.uuid4().hex}{file_extension}"
            
            # Guardar archivo
            file_path = os.path.join('products', unique_filename)
            saved_path = default_storage.save(file_path, ContentFile(image_file.read()))
            
            # Crear URL completa
            image_url = request.build_absolute_uri(settings.MEDIA_URL + saved_path)
            image_urls = [image_url]
            
        elif image_option == 'url' and request.POST.get('image_url'):
            # Usar nueva URL proporcionada
            image_urls = [request.POST.get('image_url')]
        # Si image_option == 'keep', mantener las imágenes actuales (no hacer nada)
        
        product_data = {
            'name': request.POST.get('name'),
            'description': request.POST.get('description'),
            'price': float(request.POST.get('price')),
            'category': request.POST.get('category'),
            'inventory_quantity': int(request.POST.get('quantity', 0)),
            'low_stock_threshold': int(request.POST.get('low_stock_threshold', 10)),
            'images': image_urls
        }
        
        response = api_client.update_product(product_id, product_data)
        
        if 'error' not in response:
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('marketplace:seller_products')
        else:
            messages.error(request, f'Error al actualizar producto: {response["error"]}')
    
    categories = ['Electrónicos', 'Ropa', 'Hogar', 'Deportes', 'Libros', 'Juguetes', 'Belleza', 'Automóviles', 'Motocicletas']
    
    context = {
        'product': product,
        'categories': categories,
    }
    return render(request, 'marketplace/edit_product.html', context)


def seller_orders(request):
    """Pedidos del vendedor."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para ver tus pedidos.')
        return redirect('marketplace:login')
    
    user_id = request.session.get('user_id')
    orders_response = api_client.get_orders_by_seller(user_id)
    
    if isinstance(orders_response, list):
        orders_list = orders_response
    elif isinstance(orders_response, dict) and 'error' not in orders_response:
        orders_list = orders_response.get('orders', [])
    else:
        orders_list = []
    
    context = {
        'orders': orders_list,
    }
    return render(request, 'marketplace/seller_orders.html', context)


def notifications(request):
    """Notificaciones del usuario."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para ver tus notificaciones.')
        return redirect('marketplace:login')
    
    user_id = request.session.get('user_id')
    notifications_response = api_client.get_notifications(user_id)
    
    notifications_list = notifications_response.get('notifications', []) if 'error' not in notifications_response else []
    
    context = {
        'notifications': notifications_list,
    }
    return render(request, 'marketplace/notifications.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def update_order_status(request):
    """Actualizar estado de un pedido (para vendedores)."""
    if not request.session.get('user_id'):
        return JsonResponse({'success': False, 'error': 'No autenticado'}, status=401)

    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
        new_status = data.get('status')

        if not order_id or not new_status:
            return JsonResponse({'success': False, 'error': 'Faltan parámetros'}, status=400)

        user_token = request.session.get('user_token')
        response = api_client.update_order_status(order_id, new_status, token=user_token)

        if 'error' in response:
            return JsonResponse({'success': False, 'error': response['error']}, status=400)

        return JsonResponse({'success': True, 'order': response})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def mark_notification_read(request, notification_id):
    """Marcar notificación como leída."""
    # Check if user is logged in via session
    if not request.session.get('user_id'):
        messages.error(request, 'Debes iniciar sesión para marcar notificaciones.')
        return redirect('marketplace:login')
    
    response = api_client.mark_notification_read(notification_id)
    
    if 'error' not in response:
        messages.success(request, 'Notificación marcada como leída.')
    
    return redirect('marketplace:notifications')


@csrf_exempt
@require_http_methods(["POST"])
def upload_images(request):
    """Subir imágenes de productos y devolver URLs."""
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    urls = []

    files = request.FILES.getlist('images')
    if not files:
        # Try single file field
        if 'image' in request.FILES:
            files = [request.FILES['image']]

    if not files:
        return JsonResponse({'error': 'No se enviaron imágenes'}, status=400)

    for image_file in files:
        if image_file.content_type not in allowed_types:
            return JsonResponse({'error': f'Tipo no válido: {image_file.content_type}'}, status=400)
        if image_file.size > 5 * 1024 * 1024:
            return JsonResponse({'error': 'Imagen demasiado grande (máx 5MB)'}, status=400)

        file_extension = os.path.splitext(image_file.name)[1].lower() or '.jpg'
        unique_filename = f"product_{uuid.uuid4().hex}{file_extension}"
        file_path = os.path.join('products', unique_filename)
        saved_path = default_storage.save(file_path, ContentFile(image_file.read()))
        url = request.build_absolute_uri(settings.MEDIA_URL + saved_path)
        urls.append(url)

    return JsonResponse({'urls': urls, 'success': True})