from django.shortcuts import render
from django.http import JsonResponse,HttpResponseNotFound,HttpResponseBadRequest,HttpResponseNotFound,HttpResponseBadRequest
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.core.mail import send_mail
from django.template.defaultfilters import floatformat
from django.http import HttpResponseRedirect
from rest_framework.parsers import JSONParser
from .serializers import MessageSerializer
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models import Q
import logging
import mercadopago
from django.db.models import Count


from .forms import *

import json
from .forms import RegistroForm

from django.shortcuts import get_object_or_404, redirect


from .models import *

from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

def index(request):
    producto = Producto.objects.order_by('id').all()

     # Formatear el precio de cada producto
    for p in producto:
        p.precio = "{:,.0f}".format(p.precio)

    return render(request, 'index.html', {'productos':producto})

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

def details(request, producto_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para acceder a este módulo.")
        return redirect('login_view')
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    cantidad_objetos = items.count()
    total = sum(item.producto.precio * item.cantidad for item in items)
    return render(request, 'product-details.html', {'producto': producto, "items":items, "total":total, "carro":cantidad_objetos})

def shop(request):
    iva_tasa = 0.19  # 19% IVA
    categoria_id = request.GET.get('categoria') 
    talla = request.GET.get('talla')
    color = request.GET.get('color')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if categoria_id:
        # Filtrar productos que contienen la categoría seleccionada
        producto = Producto.objects.filter(categoria=categoria_id).distinct()
    else:
        producto = Producto.objects.order_by('id').all()

    # Filtrar productos por talla si se proporciona un valor de talla
    if talla:
        producto = producto.filter(talla=talla).distinct()

    # Filtrar productos por color si se proporciona un valor de color
    if color:
        producto = producto.filter(color=color).distinct()
    
    # Filtrar productos por precio si se proporcionan valores de precio
    if min_price and max_price:
        producto = producto.filter(precio__gte=min_price, precio__lte=max_price).distinct()

    # Formatear el precio de cada producto con IVA del 19%
    for p in producto:
        precio_con_iva = p.precio * 1.19
        p.precio = "{:,.0f}".format(precio_con_iva)

    # Obtener categorías, colores y tallas con conteo de productos
    categorias = Categorias.objects.annotate(product_count=Count('producto'))
    colores = Colors.choices
    tallas_dict = {talla: display_name for talla, display_name in Tallas.choices}

    # Contar productos por color y talla
    productos_por_color = Producto.objects.values('color').annotate(product_count=Count('id'))
    productos_por_talla = Producto.objects.values('talla').annotate(product_count=Count('id'))

    # Configuración de la paginación
    paginator = Paginator(producto, 9)  # Mostrar 9 productos por página
    page_number = request.GET.get('page')  # Obtener el número de página actual
    page_obj = paginator.get_page(page_number)  # Obtener el objeto de la página actual
    
    if request.user.is_authenticated:
        carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
        items = carrito.items.all()
        total = sum(item.producto.precio for item in items)  # Sumar los precios ya con IVA
        total_formateado = "{:,.0f}".format(total)  # Formatear el total sin agregarle el IVA nuevamente
        for c in items:
            producto = c.producto
            precio_sin_iva = producto.precio
            iva = precio_sin_iva * iva_tasa
            precio_con_iva = precio_sin_iva + iva
            # Actualizar el precio del producto con IVA
            producto.precio_con_iva = "{:,.0f}".format(precio_con_iva)
            
    else:
        carrito = []
        items = []
        total_formateado = 0
    
    # Convertir a valores predeterminados si no hay productos
    min_price = min_price or 1000
    max_price = max_price or 250000

    return render(
        request, 
        'catalogo.html', 
        {
            'page_obj': page_obj,
            'paginator': paginator,
            'items': items,
            'total': total_formateado,
            'categorias': categorias,
            'colores': colores,
            'tallas': tallas_dict,
            'productos_por_color': productos_por_color,
            'productos_por_talla': productos_por_talla,
            'min_price': min_price,
            'max_price': max_price,
        })


def contact(request):
    return render(request, 'contact.html')

def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para acceder a este módulo.")
        return redirect('login_view')
    email = request.user.email
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()

    iva_tasa = 0.19  # 19% IVA

    total = 0  # Inicializa el total

    for c in items:
        producto = c.producto
        precio_sin_iva = producto.precio
        iva = precio_sin_iva * iva_tasa
        precio_con_iva = precio_sin_iva + iva

        # Actualizar el precio del producto con IVA y formatear
        producto.precio_con_iva = "{:,.0f}".format(precio_con_iva)

        # Sumar el precio con IVA al total
        total += precio_con_iva * c.cantidad

    # Formatear el total
    total_formateado = "{:,.0f}".format(total)

    cantidad_objetos = items.count()

    return render(
        request,
        'checkout.html',
        {
            'items': items,
            'total': total_formateado,
            'carro': cantidad_objetos,
            'email':email
        }
    )



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

def listar_productos(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para acceder a este módulo.")
        return redirect('login_view')
    productos = Producto.objects.all()
    return render(request, 'listar_productos.html', {"productos":productos})

def eliminar_producto(request, producto_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para acceder a este módulo.")
        return redirect('login_view')
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
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para acceder a este módulo.")
        return redirect('login_view')
    
    producto = get_object_or_404(Producto, id=id)
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    
    # Obtener la cantidad del formulario
    cantidad = int(request.POST.get('cantidad', 1))

    # Intenta obtener el objeto ItemCarrito para el producto y carrito
    try:
        item_carrito = ItemCarrito.objects.get(producto=producto, carrito=carrito)
        # Si el objeto ya existe, simplemente incrementa la cantidad
        item_carrito.cantidad += cantidad
        item_carrito.save()
        messages.success(request, 'Producto agregado al carrito')
    except ItemCarrito.DoesNotExist:
        # Si el objeto no existe, créalo y agréguelo al carrito
        item_carrito = ItemCarrito.objects.create(producto=producto, cantidad=cantidad)
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
    items = carrito.items.all().order_by('id')

    iva_tasa = 0.19  # 19% IVA
    total_con_iva = 0

    # Manejo de la cantidad
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        accion = request.POST.get('accion')

        if producto_id and accion:
            item = carrito.items.get(producto__id=producto_id)
            if accion == 'aumentar':
                item.cantidad += 1
                item.save()
            elif accion == 'disminuir' and item.cantidad > 1:
                item.cantidad -= 1
                item.save()
            return redirect('ver_carrito')  # Recargar la página para reflejar los cambios

    # Cálculo de precios con IVA
    for c in items:
        producto = c.producto
        precio_sin_iva = producto.precio
        iva = precio_sin_iva * iva_tasa
        precio_con_iva = precio_sin_iva + iva

        # Actualizar el precio del producto con IVA
        producto.precio_con_iva = "{:,.0f}".format(precio_con_iva)
        # Sumar el precio con IVA al total
        total_con_iva += precio_con_iva * c.cantidad

    # Formatear el total
    total_con_iva_formateado = "{:,.0f}".format(total_con_iva)

    return render(request, 'cart.html', {'items': items, 'total': total_con_iva_formateado})


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
    total_impuesto = total * 1.19  # Incrementar el total en un 19%

    # Formatear el precio total y el precio total con impuesto
    total_formateado = "{:,.0f}".format(total)
    total_impuesto_formateado = "{:,.0f}".format(total_impuesto)

    return total_formateado, total_impuesto_formateado

def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Este correo electrónico ya está registrado.')
            else:
                # Verificar si las contraseñas coinciden
                password = form.cleaned_data.get('password1')
                password_confirmacion = request.POST.get('password2')
                if password == password_confirmacion:
                    form.save()
                    messages.success(request, 'Registro Exitoso')
                    return redirect('login_view')
                else:
                    messages.error(request, 'Las contraseñas no coinciden.')
        else:
            messages.error(request, 'Por favor, corrige los errores.')

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

    return redirect('login_view')

@login_required(login_url='login_view')
def cerrar_sesion(request):
    logout(request)
    messages.success(request, 'Has Cerrado La Sesion Exitosamente')
    form = RegistroForm()
    return render(request, 'login.html', {'form':form})

def editar_usuario(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Debes iniciar sesión para acceder a este módulo.")
        return redirect('login_view')
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
        messages = Message.objects.filter(
            Q(sender_id=sender, receiver_id=receiver) | Q(sender_id=receiver, receiver_id=sender),
            is_read=False
        )

        return render(request, 'chat.html', {'messages': messages, 'sender': sender, 'receiver': receiver, 'users': User.objects.exclude(username=request.user.username)})

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
    
def categorias(request):
    categoria = Categorias.objects.all()
    return render(request, 'categorias.html', {'categorias':categoria})

def detalles_venta(request):
        if request.method == 'POST':
            #obtener productos del formulario
            ids_productos = request.POST.getlist('id_producto')
            nombres_productos = request.POST.getlist('nombre_producto')
            cantidad_productos = request.POST.getlist('cantidad_producto')
            precio_producto = request.POST.getlist('precio_producto')
            descripcion_producto = request.POST.getlist('descripcion_producto')
            #obtener datos del cliente
            name_user = request.POST['name_user']
            apellido_user = request.POST['apellido_user']
            tipo_documento = request.POST['tipo_documento']
            numero_documento = request.POST['numero_documento']
            direccion_user = request.POST['direccion_user']
            direccion_split = direccion_user.split('#')
            email_user = request.POST['email_user']
            celular_user = request.POST['celular_user']
            # separar direccion
            street_name = direccion_split[0].strip()
            street_number = direccion_split[1].split('-')[0].strip()  
            # zip_code 
            zip_code = request.POST.get('zip_code', '000000')
            
            items_preference = []

            for i in range(len(ids_productos)):
                # Reemplazar la coma por punto y convertir a float
                precio = precio_producto[i].replace(',', '')
                item = {
                    "id": ids_productos[i],
                    "title": nombres_productos[i],
                    "currency_id": "BRL",
                    "picture_url": "https://www.mercadopago.com/org-img/MP3/home/logomp3.gif",
                    "description": descripcion_producto[i],
                    "category_id": "art",
                    "quantity": int(cantidad_productos[i]), 
                    "unit_price": int(precio)
                }
                items_preference.append(item)
            
        sdk = mercadopago.SDK("APP_USR-5028953217533546-080114-c52fc275c338c9de19c4d7cefd88bead-1691666992")
        # crear una preferencia
        preference_data = {
            "items": items_preference,
            "payer": {
                "name": f"{name_user}",
                "surname": f"{apellido_user}",
                "email": f"{email_user}",
                "phone": {
                    "area_code": "57",
                    "number": f"{celular_user}"
                },
                "identification": {
                    "type": f"{tipo_documento}",
                    "number": f"{numero_documento}"
                },
                "address": {
                    "street_name": f"{street_name}",
                    "street_number": street_number,
                    "zip_code": f"{zip_code}"
                }
            },
            "back_urls": {
                "success": "https://www.success.com",
                "failure": "http://www.failure.com",
                "pending": "http://www.pending.com"
            },
            "auto_return": "approved",
            "payment_methods": {
            "excluded_payment_methods" : [],
            "excluded_payment_types" : [],
            "installments" : 12
            },
            "notification_url": "https://msf-cktv.onrender.com/notifications/",
            "statement_descriptor": "MSF",
            "external_reference": "Reference_1234",
        }
        #obtener respuesta
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        contexto = {
            'preference_id': preference['id'],
            'name_user':name_user
        }
        return render(request, 'metodo_pago.html', contexto)

@csrf_exempt
def notifications_pay(request):
    if request.method == 'POST':
        sdk = mercadopago.SDK("APP_USR-5028953217533546-080114-c52fc275c338c9de19c4d7cefd88bead-1691666992")
        # Procesa la notificación de Mercado Pago
        data = json.loads(request.body)
        
        if data.get('type') == 'payment' and 'data' in data:
            payment_id = data['data']['id']  # Obtén el ID del pago
            
            # Consulta los detalles del pago usando el SDK de Mercado Pago
            payment_info = sdk.payment().get(payment_id)
            status = payment_info['response']['status']  # Obtén el estado del pago

            if status == 'approved':
                # Obtener la información de productos, cliente y orden
                additional_info = payment_info['response'].get('additional_info', {})
                payer_info = additional_info.get('payer', {})
                items_info = additional_info.get('items', [])

                # Crear el contenido del correo
                productos = "\n".join([f"Producto: {item['title']} - Cantidad: {item['quantity']} - Precio: {item['unit_price']}" for item in items_info])
                cliente = f"{payer_info['first_name']} {payer_info['last_name']}\nDirección: {payer_info['address']['street_name']} #{payer_info['address']['street_number']}\nEmail: {payment_info['response']['payer']['email']}\nTeléfono: {payer_info['phone']['area_code']}-{payer_info['phone']['number']}"

                # Enviar el correo tanto al cliente como a modasinfronteras2@gmail.com
                send_mail(
                    subject="Confirmación de pago exitoso",
                    message=f"Estimado {payer_info['first_name']},\n\nSu pago ha sido aprobado exitosamente.\n\nInformación de la orden:\n{productos}\n\nInformación personal:\n{cliente}\n\nGracias por su compra.",
                    from_email="modasinfronteras2@gmail.com",
                    recipient_list=['modasinfronteras2@gmail.com'],
                    fail_silently=False,
                )

                print("PAGO CON ÉXITO y correo enviado.")

        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'error': 'invalid request'}, status=400)