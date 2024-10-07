# nutrition/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import *



class PatientRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        
        if password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data

class DoctorRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        
        if password != password_confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        
        return cleaned_data

class PasswordResetForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        # Validar que el nombre de usuario y el email coincidan en la base de datos
        from django.contrib.auth.models import User
        if not User.objects.filter(username=username, email=email).exists():
            raise forms.ValidationError("El nombre de usuario y el correo electrónico no coinciden.")
        return cleaned_data
    
class PatientProfileForm(forms.ModelForm):
        class Meta:
            model = PatientProfile
            fields = ['birth_date', 'phone_number', 'weight', 'gender', 'allergies', 'intolerances', 'food_preferences']

class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = DoctorProfile
        fields = ['phone_number', 'email', 'specialty', 'medical_license', 'clinic_address']

class PersonalInfoForm(forms.ModelForm):
    class Meta:
        model = PersonalInfo
        fields = ['nombre_contacto_emergencia', 'relacion_contacto_emergencia', 'numero_emergencia','direccion', 'curp']  # Campos necesarios
        labels = {
            'nombre_contacto_emergencia': 'Nombre completo del Contacto de Emergencia',
            'relacion_contacto_emergencia': 'Relación con el Contacto de Emergencia',
            'numero_emergencia': 'Número de Emergencia',
            'direccion': 'Dirección',
            'curp': 'Curp',
        }
        

class DisponibilidadForm(forms.ModelForm):
    class Meta:
        model = DisponibilidadDoctor
        fields = ['dia', 'hora_inicio', 'hora_fin']








class AgendarCitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ['doctor', 'fecha', 'hora']

    # Validar la disponibilidad del doctor en la fecha y hora seleccionadas
    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        fecha = cleaned_data.get('fecha')
        hora = cleaned_data.get('hora')

        if Cita.objects.filter(doctor=doctor, fecha=fecha, hora=hora).exists():
            raise forms.ValidationError('El doctor no está disponible en la fecha y hora seleccionadas.')
        
        return cleaned_data
    



class NotaForm(forms.ModelForm):
    class Meta:
        model = Nota
        fields = ['contenido']

