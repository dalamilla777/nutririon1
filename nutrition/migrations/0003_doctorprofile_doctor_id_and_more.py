# Generated by Django 5.1 on 2024-09-19 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0002_remove_doctorprofile_doctor_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctorprofile',
            name='doctor_id',
            field=models.CharField(default='710d9e2892', editable=False, max_length=10, unique=True),
        ),
        migrations.AddField(
            model_name='patientprofile',
            name='dietary_restrictions',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='patientprofile',
            name='height',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='patientprofile',
            name='nutrition_goals',
            field=models.TextField(blank=True, null=True),
        ),
    ]
