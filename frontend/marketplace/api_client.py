"""
Cliente para comunicarse con la API FastAPI del backend.
"""
import requests
import json
from django.conf import settings
from typing import Dict, List, Optional, Any


class APIClient:
    """Cliente para interactuar con la API FastAPI."""
    
    def __init__(self):
        self.base_url = settings.API_BASE_URL
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, 
                     headers: Dict = None, params: Dict = None, token: str = None) -> Dict:
        """Realizar petición HTTP a la API."""
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {'Content-Type': 'application/json'}
        if headers:
            default_headers.update(headers)
        
        # Add token to headers if provided
        if token:
            default_headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, headers=default_headers, params=params)
            elif method.upper() == 'POST':
                response = self.session.post(url, headers=default_headers, 
                                           json=data, params=params)
            elif method.upper() == 'PUT':
                response = self.session.put(url, headers=default_headers, json=data)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, headers=default_headers, json=data, params=params)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=default_headers)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Error en petición API: {method} {url}")
            print(f"Status Code: {e.response.status_code if hasattr(e, 'response') and e.response else 'N/A'}")
            print(f"Error: {e}")
            try:
                if hasattr(e, 'response') and e.response:
                    print(f"Response: {e.response.text}")
            except:
                pass
            return {'error': str(e)}
    
    def set_auth_token(self, token: str):
        """Establecer token de autenticación."""
        self.session.headers.update({'Authorization': f'Bearer {token}'})
    
    def clear_auth_token(self):
        """Limpiar token de autenticación."""
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    # Métodos de usuarios
    def register_user(self, user_data: Dict) -> Dict:
        """Registrar nuevo usuario."""
        return self._make_request('POST', '/api/v1/users/register', data=user_data)
    
    def login_user(self, email: str, password: str) -> Dict:
        """Iniciar sesión."""
        data = {'email': email, 'password': password}
        return self._make_request('POST', '/api/v1/users/login', data=data)
    
    def get_user_profile(self, user_id_or_endpoint: str, token: str = None) -> Dict:
        """Obtener perfil de usuario."""
        if user_id_or_endpoint == 'profile':
            # Usar endpoint de perfil actual
            return self._make_request('GET', '/api/v1/users/profile', token=token)
        else:
            # Usar endpoint específico por ID
            return self._make_request('GET', f'/api/v1/users/{user_id_or_endpoint}', token=token)
    
    def update_user_profile(self, user_id: str, profile_data: Dict, token: str = None) -> Dict:
        """Actualizar perfil de usuario."""
        return self._make_request('PUT', f'/api/v1/users/{user_id}', data=profile_data, token=token)
    
    # Métodos de productos
    def get_products(self, page: int = 1, page_size: int = 12) -> Dict:
        """Obtener lista de productos."""
        params = {'page': page, 'page_size': page_size}
        return self._make_request('GET', '/api/v1/products/', params=params)
    
    def get_product(self, product_id: str) -> Dict:
        """Obtener producto específico."""
        return self._make_request('GET', f'/api/v1/products/{product_id}')
    
    def create_product(self, product_data: Dict, token: str = None) -> Dict:
        """Crear nuevo producto."""
        return self._make_request('POST', '/api/v1/products/', data=product_data, token=token)
    
    def update_product(self, product_id: str, product_data: Dict, token: str = None) -> Dict:
        """Actualizar producto."""
        return self._make_request('PUT', f'/api/v1/products/{product_id}', data=product_data, token=token)
    
    def search_products(self, query: str = None, category: str = None, 
                       min_price: float = None, max_price: float = None,
                       page: int = 1, page_size: int = 12) -> Dict:
        """Buscar productos."""
        params = {'page': page, 'page_size': page_size}
        if query:
            params['q'] = query
        if category:
            params['category'] = category
        if min_price:
            params['min_price'] = min_price
        if max_price:
            params['max_price'] = max_price
        
        return self._make_request('GET', '/api/v1/products/search', params=params)
    
    def get_products_by_seller(self, seller_id: str, token: str = None) -> Dict:
        """Obtener productos de un vendedor."""
        return self._make_request('GET', f'/api/v1/products/seller/{seller_id}', token=token)
    
    # Métodos de carrito
    def get_cart(self, user_id: str, token: str = None) -> Dict:
        """Obtener carrito del usuario."""
        return self._make_request('GET', '/api/v1/orders/cart', token=token)
    
    def add_to_cart(self, user_id: str, product_id: str, quantity: int) -> Dict:
        """Agregar producto al carrito."""
        data = {'product_id': product_id, 'quantity': quantity}
        return self._make_request('POST', '/api/v1/orders/cart/items', data=data)
    
    def update_cart_item(self, user_id: str, product_id: str, quantity: int) -> Dict:
        """Actualizar cantidad en carrito."""
        data = {'quantity': quantity}
        return self._make_request('PUT', f'/api/v1/orders/cart/items/{product_id}', data=data)
    
    def remove_from_cart(self, user_id: str, product_id: str) -> Dict:
        """Eliminar producto del carrito."""
        return self._make_request('DELETE', f'/api/v1/orders/cart/items/{product_id}')
    
    # Métodos de pedidos
    def create_order(self, order_data: Dict, token: str = None) -> Dict:
        """Crear nuevo pedido."""
        return self._make_request('POST', '/api/v1/orders/', data=order_data, token=token)
    
    def get_orders_by_buyer(self, buyer_id: str) -> Dict:
        """Obtener pedidos del comprador."""
        return self._make_request('GET', '/api/v1/orders/')
    
    def get_orders_by_seller(self, seller_id: str) -> Dict:
        """Obtener pedidos del vendedor."""
        return self._make_request('GET', '/api/v1/orders/')
    
    def get_order(self, order_id: str) -> Dict:
        """Obtener pedido específico."""
        return self._make_request('GET', f'/api/v1/orders/{order_id}')
    
    def update_order_status(self, order_id: str, status: str, token: str = None) -> Dict:
        """Actualizar estado del pedido."""
        params = {'status': status}
        return self._make_request('PATCH', f'/api/v1/orders/{order_id}/status', params=params, token=token)
    
    # Métodos de pagos
    def process_payment(self, payment_data: Dict) -> Dict:
        """Procesar pago."""
        return self._make_request('POST', '/payments/process', data=payment_data)
    
    def get_payment_methods(self) -> Dict:
        """Obtener métodos de pago disponibles."""
        return self._make_request('GET', '/payments/methods')
    
    # Métodos de notificaciones
    def get_notifications(self, user_id: str) -> Dict:
        """Obtener notificaciones del usuario."""
        return self._make_request('GET', f'/notifications/{user_id}')
    
    def mark_notification_read(self, notification_id: str) -> Dict:
        """Marcar notificación como leída."""
        return self._make_request('PUT', f'/notifications/{notification_id}/read')
    
    def send_notification(self, notification_data: Dict) -> Dict:
        """Enviar notificación."""
        return self._make_request('POST', '/notifications/', data=notification_data)


# Instancia global del cliente API
api_client = APIClient()