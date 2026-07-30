"""Context processors para el marketplace."""

from .api_client import api_client


def cart_context(request):
    """Agregar información del carrito a todas las plantillas."""
    cart_count = 0
    
    # Solo obtener el carrito si el usuario está autenticado
    if request.session.get('user_id'):
        try:
            user_token = request.session.get('user_token')
            cart_response = api_client.get_cart(request.session.get('user_id'), token=user_token)
            if cart_response and 'error' not in cart_response and isinstance(cart_response, dict) and cart_response.get('items'):
                # Contar total de items (sumando cantidades)
                cart_count = sum(item.get('quantity', 0) for item in cart_response['items'])
        except Exception as e:
            # Si hay error, simplemente dejar el contador en 0
            print(f"Error al obtener carrito: {e}")
            pass
    
    return {
        'cart_count': cart_count
    }
