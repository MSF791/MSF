# Generated by Django 5.0.1 on 2024-02-20 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appEcommerce', '0011_alter_producto_descripcion'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='en_lista_deseos',
            field=models.BooleanField(default=False),
        ),
    ]
