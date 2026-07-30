from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    # Páginas principales
    path('', views.home, name='home'),
    path('productos/', views.products, name='products'),
    path('producto/<str:product_id>/', views.product_detail, name='product_detail'),
    path('buscar/', views.search, name='search'),
    
    # Autenticación
    path('registro/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.profile, name='profile'),
    
    # Carrito y pedidos
    path('carrito/', views.cart, name='cart'),
    path('carrito/agregar/<str:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('carrito/actualizar/', views.update_cart, name='update_cart'),
    path('carrito/eliminar/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('pedidos/', views.orders, name='orders'),
    path('pedido/<str:order_id>/', views.order_detail, name='order_detail'),
    
    # Vendedor
    path('vendedor/', views.seller_dashboard, name='seller_dashboard'),
    path('vendedor/productos/', views.seller_products, name='seller_products'),
    path('vendedor/producto/nuevo/', views.create_product, name='create_product'),
    path('vendedor/producto/<str:product_id>/editar/', views.edit_product, name='edit_product'),
    path('vendedor/pedidos/', views.seller_orders, name='seller_orders'),
    path('vendedor/pedidos/actualizar-estado/', views.update_order_status, name='update_order_status'),
    
    # Notificaciones
    path('notificaciones/', views.notifications, name='notifications'),
    path('notificaciones/marcar-leida/<str:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
]