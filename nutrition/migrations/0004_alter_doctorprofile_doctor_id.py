# Generated by Django 5.1 on 2024-09-19 18:29

import nutrition.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0003_doctorprofile_doctor_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctorprofile',
            name='doctor_id',
            field=models.CharField(default=nutrition.models.generate_doctor_id, editable=False, max_length=10, unique=True),
        ),
    ]