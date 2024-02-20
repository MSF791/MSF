#django
from django import forms

#predio
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta: 
        model = Producto
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        """
        se usa para agregar la clase form-control a todos los elementos del form
        """
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'