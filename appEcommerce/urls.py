from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('shop/', shop, name='shop'),
    path('contact', contact, name='contact'),
    path('check/', checkout, name='check'),
    path('productos/', productos, name='productos'),
    path('create_producto', create_producto, name='create_producto'),
    path('agregar_al_carrito/<int:id>/', agregar_al_carrito, name='agregar_al_carrito'),
    path('ver_carrito', ver_carrito, name="ver_carrito"),
    path('actualizar_carrito', actualizar_carrito, name="actualizar_carrito"),
    path('quitar_del_carrito/<int:producto_id>/', quitar_del_carrito, name='quitar_del_carrito'),
    path('details/<int:producto_id>/', details, name='details'),
    path('login_view', login_view, name='login_view'),
    path('deseos', deseos, name='deseos'),
    path('agregar_a_deseos/<int:id>/', agregar_a_deseos, name='agregar_a_deseos'),
    path('eliminar_de_deseos/<int:id>/', eliminar_de_deseos, name='eliminar_de_deseos'),
    path('listar_productos',listar_productos,name='listar_productos'),
    path('chat/', chat, name='chat'),
    path('enviar_mensaje/', enviar_mensaje, name='enviar_mensaje'),
    path('registrar/', registrar_usuario, name='registrar_usuario'),
    path('iniciar_sesion/', iniciar_sesion, name='iniciar_sesion'),
    path('cerrar_sesion/', cerrar_sesion, name='cerrar_sesion'),
    path('verificar_autenticacion/', verificar_autenticacion, name='verificar_autenticacion'),
    path('eliminar_producto/<int:producto_id>/', eliminar_producto, name='eliminar_producto'),
    path('editar_producto/<int:producto_id>/', editar_producto, name='editar_producto'),
    path('account', editar_usuario, name='editar_usuario'),
    path('password', recuperar_contraseña, name='password'),
    path('reset_password/<str:token>/<str:email>/', reset_password, name='reset_password')
]
