#django
from django import forms

#modelos
from .models import *

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

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

class RegistroForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class Password(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email']

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verificar si el correo electrónico está asociado a algún usuario
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('No se encontró ninguna cuenta asociada a este correo electrónico.')
        return email
    
class ResetPasswordForm(forms.Form):
    password = forms.CharField(label='Nueva Contraseña', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirmar Nueva Contraseña', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden. Por favor, inténtalo de nuevo.")

        # Validar la contraseña usando las herramientas de validación de Django
        try:
            validate_password(password)
        except forms.ValidationError as e:
            self.add_error('password', e)

        return cleaned_data
    
from django import forms

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sender', 'receiver', 'message']

