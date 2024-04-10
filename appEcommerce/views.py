from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from rest_framework.parsers import JSONParser
from .serializers import MessageSerializer
from django.core.paginator import Paginator
import logging


from .forms import *

import json
from .forms import RegistroForm

from django.shortcuts import get_object_or_404, redirect


from .models import *

from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'index.html')

def verificar_autenticacion(request):
    if request.user.is_authenticated:
        return JsonResponse({'authenticated': True})
    else:
        return JsonResponse({'authenticated': False})

@csrf_exempt
def enviar_mensaje(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        mensaje = data.get('mensaje', '')
        
        # Aquí podrías realizar algún procesamiento adicional si es necesario

        respuesta = {'mensaje': 'Mensaje recibido por el servidor'}
        return JsonResponse(respuesta)

    return JsonResponse({'error': 'Método no permitido'}, status=405)

def agregar_a_deseos(request, id):
    producto = get_object_or_404(Producto, id=id)

    # Cambia el estado del campo en_lista_deseos del producto
    producto.en_lista_deseos = not producto.en_lista_deseos
    producto.save()
    messages.success(request, 'Se Ha Agregado A Tu Lista De Deseos')

    return redirect('shop')

def eliminar_de_deseos(request, id):
    producto = get_object_or_404(Producto, id=id)

    # Cambia el estado del campo en_lista_deseos del producto
    producto.en_lista_deseos = False
    producto.save()

    return redirect('deseos')

def deseos(request):
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    cantidad_objetos = items.count()
    productos_deseados = Producto.objects.filter(en_lista_deseos=True)
    return render(request, 'deseos.html', {"items":items, "carro":cantidad_objetos, "productos_deseados": productos_deseados})


def login_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Puedes redirigir a la página de inicio de sesión después del registro
    else:
        form = RegistroForm()

    return render(request, 'login.html', {'form': form})

@login_required(login_url='login_view')
def details(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    cantidad_objetos = items.count()
    total = sum(item.producto.precio * item.cantidad for item in items)
    return render(request, 'product-details.html', {'producto': producto, "items":items, "total":total, "carro":cantidad_objetos})

def shop(request):
    producto = Producto.objects.all()

    # Configuración de la paginación
    paginator = Paginator(producto, 9)  # Mostrar 9 productos por página
    page_number = request.GET.get('page')  # Obtener el número de página actual
    page_obj = paginator.get_page(page_number)  # Obtener el objeto de la página actual
    return render(request, 'shop.html', {'page_obj':page_obj, 'paginator':paginator})

def contact(request):
    return render(request, 'contact.html')

@login_required(login_url='login_view')
def checkout(request):
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    cantidad_objetos = items.count()
    total = calcular_nuevo_total(carrito)
    return render(request, 'checkout.html',{'items': items, 'total': total, "carro":cantidad_objetos})

def productos(request):
    return render(request, 'registrar_producto.html')

def create_producto(request):
    mensaje = None
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        #si el formulario es valido pasa los datos
        if form.is_valid():
            productoGuardado = Producto(
                nombre=form.cleaned_data['nombre'],
                descripcion=form.cleaned_data['descripcion'],
                precio=form.cleaned_data['precio'],
                stock=form.cleaned_data['stock'],
                imagen=form.cleaned_data['imagen']
            )
            productoGuardado.save()
            mensaje='Producto Creado Con Exito'
        else:
            pass
    else:
        form = ProductoForm()
    return render(request, 'registrar_producto.html', {'form': form, 'mensaje':mensaje})

@login_required(login_url='login_view')
def listar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'listar_productos.html', {"productos":productos})

@login_required(login_url='login_view')
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    producto.delete()
    messages.success(request, 'el producto se ha eliminado con exito')
    return redirect('listar_productos')

def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            return redirect('listar_productos')  
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'editar_producto.html', {'form': form, 'producto': producto})

def agregar_al_carrito(request, id):
    producto = get_object_or_404(Producto, id=id)
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)

    # Intenta obtener el objeto ItemCarrito para el producto y carrito
    try:
        item_carrito = ItemCarrito.objects.get(producto=producto, carrito=carrito)
        # Si el objeto ya existe, simplemente incrementa la cantidad
        item_carrito.cantidad += 1
        item_carrito.save()
        messages.success(request,'Producto Agregado Al Carrito')
    except ItemCarrito.DoesNotExist:
        # Si el objeto no existe, créalo y agréguelo al carrito
        item_carrito = ItemCarrito.objects.create(producto=producto, cantidad=1)
        carrito.items.add(item_carrito)
    return redirect('shop')

def quitar_del_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    carrito = Carrito.objects.get(usuario=request.user)

    try:
        item_carrito = carrito.items.get(producto=producto)
        item_carrito.cantidad -= 1

        if item_carrito.cantidad < 1:
            carrito.items.remove(item_carrito)
        else:
            item_carrito.save()

    except ItemCarrito.DoesNotExist:
        pass

    return redirect('ver_carrito')

def ver_carrito(request):
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    total = calcular_nuevo_total(carrito)

    return render(request, 'cart.html', {'items': items, 'total': total})

def actualizar_carrito(request):
    if request.method == 'POST':
        item_id = request.POST.get('itemId')
        cantidad = int(request.POST.get('cantidad', 0))

        # Obtener o crear la instancia de Carrito para el usuario actual
        carrito, creado = Carrito.objects.get_or_create(usuario=request.user)

        # Lógica para actualizar la cantidad del ítem en el carrito
        try:
            item_carrito = carrito.items.get(id=item_id)
            item_carrito.cantidad = cantidad
            item_carrito.save()

            # Calcular el nuevo subtotal y total
            nuevo_subtotal = item_carrito.producto.precio * cantidad
            nuevo_total = calcular_nuevo_total(carrito)

            return JsonResponse({'subtotal': nuevo_subtotal, 'total': nuevo_total})
        except Exception as e:
            print(f'Error: {e}')
            return JsonResponse({'error': str(e)})

    return JsonResponse({'error': 'Invalid request'})

def calcular_nuevo_total(carrito):
    # Aquí debes calcular el nuevo total basado en los ítems del carrito
    items = carrito.items.all()
    total = sum(item.producto.precio * item.cantidad for item in items)
    return total

def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registro Exitoso')
            return redirect('login_view')  # Puedes redirigir a la página de inicio de sesión después del registro
    else:
        form = RegistroForm()

    return render(request, 'login.html', {'form': form})

def iniciar_sesion(request):
    form = RegistroForm()

    if request.method == 'POST':
        usuario = request.POST['usuario']
        contrasena = request.POST['contrasena']
        user = authenticate(request, username=usuario, password=contrasena)

        if user is not None:
            login(request, user)

            messages.success(request, 'Has iniciado sesión con éxito.')
            return redirect('login_view')
        else:
            try:
                user = User.objects.get(username=usuario)
                if not user.check_password(contrasena):
                    messages.error(request, 'El Usuario O Contraseña Es Incorrecta.')
                else:
                    messages.error(request, 'La cuenta está desactivada.')
            except User.DoesNotExist:
                messages.error(request, 'El Usuario O Contraseña Es Incorrecta.')

    return render(request, 'login.html', {'form': form})

@login_required(login_url='login_view')
def cerrar_sesion(request):
    logout(request)
    messages.success(request, 'Has Cerrado La Sesion Exitosamente')
    form = RegistroForm()
    return render(request, 'login.html', {'form':form})

@login_required(login_url='login_view')
def editar_usuario(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Se Ha Actualizado El Usuario Con Exito')
            return render(request, 'edit_user.html', {'form': form})
    else:
        form = UserEditForm(instance=request.user)
    
    return render(request, 'edit_user.html', {'form': form})

def recuperar_contraseña(request):
    mensaje_error = None  
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = get_user_model().objects.filter(email=email).first()
            if user:
                # Generar el token de recuperación de contraseña y enviar el correo electrónico
                token = default_token_generator.make_token(user)
                reset_link = request.build_absolute_uri(reverse('reset_password', kwargs={'token': token, 'email':email}))
                send_password_reset_email(user.email, reset_link)
                return render(request, 'reset_password_done.html')
            else:
                # El correo electrónico no está asociado a ningún usuario
                mensaje_error = 'No se encontró ningún usuario con este correo electrónico.'
        else:
            mensaje_error = 'No se encontró ningún usuario con este correo electrónico.'
    else:
        form = PasswordResetForm()
    return render(request, 'recuperar_contraseña_correo.html', {'form': form, 'mensaje': mensaje_error})


def send_password_reset_email(email, reset_link):
    subject = 'Restablecer contraseña'
    message = f'Haga clic en el siguiente enlace para restablecer su contraseña: {reset_link}'
    sender_email = 'modasinfronteras2@gmail.com'  # Reemplaza esto con tu dirección de correo electrónico
    recipient_list = [email]
    
    send_mail(subject, message, sender_email, recipient_list)
    return email

def reset_password(request, token, email):
    # Obtener el usuario asociado al correo electrónico
    user = get_user_model().objects.filter(email=email).first()

    if not user or not default_token_generator.check_token(user, token):
        # Si no se encuentra el usuario o el token no es válido, redirigir a una página de error
        return render(request, 'reset_password_error.html')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            # Procesar el formulario de restablecimiento de contraseña
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()

            return render(request, 'password_reset_complete.html')
    else:
        form = ResetPasswordForm()

    return render(request, 'reset_password.html', {'form': form})

def chat_view(request):
    if not request.user.is_authenticated:
        return redirect('login_view')
    if request.method == "GET":
        return render(request, 'chat.html',
                      {'users': User.objects.exclude(username=request.user.username)})
    
def message_view(request, sender, receiver):
    if not request.user.is_authenticated:
        return redirect('login_view')
    if request.method == "GET":
        return render(request, "messages.html",
                      {'users': User.objects.exclude(username=request.user.username),
                       'receiver': User.objects.get(id=receiver),
                       'messages': Message.objects.filter(sender_id=sender, receiver_id=receiver) |
                                   Message.objects.filter(sender_id=receiver, receiver_id=sender)})
    
@csrf_exempt
def message_list(request, sender=None, receiver=None):
    """
    List all required messages, or create a new message.
    """
    if request.method == 'GET':
        messages = Message.objects.filter(sender_id=sender, receiver_id=receiver, is_read=False)
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        for message in messages:
            message.is_read = True
            message.save()
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


