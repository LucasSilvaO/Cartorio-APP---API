# Generated by Django 4.2.7 on 2025-01-26 13:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dados', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='usuario',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Usuario', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('admin', 'Admin'), ('cliente', 'Cliente'), ('colaborador', 'Colaborador'), ('comercial', 'Comercial'), ('vendedor', 'Vendedor'), ('financeiro', 'Financeiro'), ('gerencia', 'Gerência')], default='cliente', max_length=20),
        ),
    ]
