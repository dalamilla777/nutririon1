import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patientprofile')
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='patients')
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    height = models.FloatField(
        null=True, 
        blank=True, 
        validators=[MinValueValidator(1.30), MaxValueValidator(2.30)]
    )
    peso = models.FloatField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')], blank=True)
    nutrition_goals = models.TextField(blank=True, null=True)
    dietary_restrictions = models.TextField(blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    intolerances = models.TextField(blank=True, null=True)
    food_preferences = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Perfil del Paciente: {self.user.username}'

def generate_doctor_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctorprofile')
    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField()
    specialty = models.CharField(max_length=255)
    medical_license = models.CharField(max_length=255)
    clinic_address = models.CharField(max_length=255, blank=True)
    doctor_id = models.CharField(max_length=10, unique=True, default=generate_doctor_id, editable=False)

    def __str__(self):
        return f'Dr. {self.user.username} - Especialidad: {self.specialty}'

class PersonalInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='personalinfo')
    nombre = models.CharField(max_length=255)
    apellidos = models.CharField(max_length=255)
    numero_emergencia = models.CharField(max_length=15, blank=True)
    nombre_contacto_emergencia = models.CharField(max_length=255, blank=True)
    relacion_contacto_emergencia = models.CharField(max_length=50, blank=True)
    direccion = models.TextField(blank=True)
    curp = models.CharField(max_length=18, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"

class DisponibilidadDoctor(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disponibilidad_doctor')
    dia = models.CharField(max_length=10, choices=[('Lunes', 'Lunes'), ('Martes', 'Martes'), ('Miércoles', 'Miércoles'), ('Jueves', 'Jueves'), ('Viernes', 'Viernes')])
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.doctor.username}: {self.dia} de {self.hora_inicio} a {self.hora_fin}"

class Cita(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_cita')
    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paciente_cita')
    fecha = models.DateField()
    hora = models.TimeField()
    estado = models.CharField(max_length=20, choices=[('Pendiente', 'Pendiente'), ('Confirmada', 'Confirmada'), ('Rechazada', 'Rechazada')], default='Pendiente')

    def __str__(self):
        return f"Cita con {self.doctor.username} el {self.fecha} a las {self.hora}"

class Nota(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_nota')
    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paciente_nota')
    contenido = models.TextField()
    fecha = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Nota de {self.doctor.username} para {self.paciente.username} - {self.fecha}"

class FoodIntake(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_intakes')
    food_item = models.CharField(max_length=255)
    quantity = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        validators=[MinValueValidator(0.0), MaxValueValidator(10000.0)]
    )
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.food_item} - {self.date} {self.time}"
    
class FoodAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Relacionar el análisis con el usuario
    calorias = models.IntegerField()
    ingredientes = models.TextField()  # Almacenar como un texto separado por comas
    es_sano = models.BooleanField()
    fecha_analisis = models.DateTimeField(auto_now_add=True)  # Fecha en que se realizó el análisis

    def __str__(self):
        return f"Análisis de {self.user.username} - {self.fecha_analisis}"
    
class IngredientAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredientes = models.TextField()  # Lista de ingredientes detectados
    recomendacion = models.TextField()  # Recomendación del platillo a preparar
    fecha_analisis = models.DateTimeField(auto_now_add=True)  # Fecha del análisis

    def __str__(self):
        return f"Análisis de ingredientes de {self.user.username} - {self.fecha_analisis}"