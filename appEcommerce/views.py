from django.shortcuts import render
from django.http import JsonResponse

from .forms import ProductoForm

from django.shortcuts import get_object_or_404, redirect

from .models import Producto, Carrito, ItemCarrito

def index(request):
    traer_productos = Producto.objects.all()
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    cantidad_objetos = items.count()
    total = calcular_nuevo_total(carrito)
    return render(request, 'index.html', {"productos":traer_productos, "items":items, "total":total, "carro":cantidad_objetos})

def agregar_a_deseos(request, id):
    producto = get_object_or_404(Producto, id=id)

    # Cambia el estado del campo en_lista_deseos del producto
    producto.en_lista_deseos = not producto.en_lista_deseos
    producto.save()

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

def login(request):
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    cantidad_objetos = items.count()
    total = sum(item.producto.precio * item.cantidad for item in items)
    return render(request, 'login.html', {"items":items, "total":total, "carro":cantidad_objetos})

def details(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    cantidad_objetos = items.count()
    total = sum(item.producto.precio * item.cantidad for item in items)
    return render(request, 'product-details.html', {'producto': producto, "items":items, "total":total, "carro":cantidad_objetos})

def shop(request):
    traer_productos = Producto.objects.all()
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    cantidad_objetos = items.count()
    total = sum(item.producto.precio * item.cantidad for item in items)
    return render(request, 'shop.html', {"productos":traer_productos, "items":items, "total":total, "carro":cantidad_objetos})

def contact(request):
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    cantidad_objetos = items.count()
    total = sum(item.producto.precio * item.cantidad for item in items)
    return render(request, 'contact.html', {"items":items, "total":total, "carro":cantidad_objetos})

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

def listar_productos(request):
    productos = Producto.objects.all()
    return render(request, 'listar_productos.html', {"productos":productos})

def agregar_al_carrito(request, id):
    producto = get_object_or_404(Producto, id=id)
    carrito, creado = Carrito.objects.get_or_create(usuario=request.user)

    # Verifica si el producto ya está en el carrito
    item_carrito, creado = ItemCarrito.objects.get_or_create(producto=producto, defaults={'cantidad': 1})

    if item_carrito in carrito.items.all():
        # Si el objeto ya existe, simplemente incrementa la cantidad
        item_carrito.cantidad += 1
        item_carrito.save()
    else:
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
    cantidad_objetos = items.count()
    total = calcular_nuevo_total(carrito)
    return render(request, 'cart.html', {'items': items, 'total': total, "carro":cantidad_objetos})

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
