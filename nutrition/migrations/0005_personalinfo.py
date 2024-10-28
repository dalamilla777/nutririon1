# Generated by Django 5.1 on 2024-09-19 20:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0004_alter_doctorprofile_doctor_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonalInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('apellidos', models.CharField(max_length=255)),
                ('contacto_emergencia', models.CharField(blank=True, max_length=15)),
                ('nombre_contacto_emergencia', models.CharField(blank=True, max_length=255)),
                ('relacion_contacto_emergencia', models.CharField(blank=True, max_length=50)),
                ('direccion', models.TextField(blank=True)),
                ('curp', models.CharField(blank=True, max_length=18)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
