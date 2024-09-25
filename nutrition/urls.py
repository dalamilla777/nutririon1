from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Página principal genérica
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),
    
    # Login para doctores
    path('login/doctor/', views.doctor_login, name='doctor_login'),

    # Login para pacientes
    path('login/patient/', views.patient_login, name='patient_login'),

    # Home del doctor y paciente
    path('home/doctor/', views.doctor_home, name='doctor_home'),
    path('home/patient/', views.patient_home, name='patient_home'),

    path('registration-successful/', views.registration_successful, name='registration_successful'),  # Agrega esta línea
    path('profile/patient/', views.patient_profile, name='patient_profile'),  # Ruta para el perfil del paciente
    path('profile/doctor/', views.doctor_profile, name='doctor_profile'),
    
    path('personal_info/', views.personal_info_view, name='personal_info'),


]
