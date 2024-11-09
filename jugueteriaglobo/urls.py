"""
URL configuration for jugueteriaglobo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from webapp import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.send_code, name='send_code'),  # Verifica que esta URL coincida con el nombre que usa el middleware
    path('validate/', views.validate_code, name='validate_code'),
    path('shop/', views.shop, name='shop'),
    path('login/', views.login_view, name='login'),
    path('two-step-auth/', views.two_step_auth_view, name='two_step_auth'),
    path('index-admin/', views.admin, name='admin'),
    path('hijos/', views.listar_hijos, name='listar_hijos'),
    path('hijos/agregar/', views.agregar_hijo, name='agregar_hijo'),
    path('hijos/editar/<int:id_cuenta>/', views.editar_hijo, name='editar_hijo'),
    path('hijos/eliminar/<int:id_cuenta>/', views.eliminar_hijo, name='eliminar_hijo'),
    path('agregar_padre/', views.agregar_padre, name='agregar_padre'),
    path('editar_padre/<int:id_cuenta>/', views.editar_padre, name='editar_padre'),
    path('productos/', views.listar_productos_admin, name='productos'),
    path('productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('productos/editar/<int:id_producto>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:id_producto>/', views.eliminar_producto, name='eliminar_producto'),
    path('logout/', views.logout_view, name='logout'),
    path('chatbot/', views.chatbot_interface, name='chatbot'),
    path("chatbot/responder", views.chatbot_responder, name="chatbot_responder"),
    path('productos-compra/', views.listar_productos, name='productos-compra'),
    path('agregar_al_carrito/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/', views.mostrar_carrito, name='carrito'),
    path('eliminar_producto_carrito/<int:producto_id>/', views.eliminar_producto_carrito, name='eliminar_producto_carrito'),
    path('realizar-venta/', views.realizar_venta, name='realizar_venta'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
