from django.urls import path
from . import views
from .views import editar_nota, ver_notas_paciente


urlpatterns = [
    # Página principal genérica
    path('', views.home, name='home'),

    # Registro
    path('register/patient/', views.register_patient, name='register_patient'),
    path('register/doctor/', views.register_doctor, name='register_doctor'),

    # Login
    path('login/doctor/', views.doctor_login, name='doctor_login'),
    path('login/patient/', views.patient_login, name='patient_login'),

    # Home del doctor y paciente
    path('home/doctor/', views.doctor_home, name='doctor_home'),
    path('home/patient/', views.patient_home, name='patient_home'),

    # Registro exitoso
    path('registration-successful/', views.registration_successful, name='registration_successful'),

    # Perfil del paciente y doctor
    path('profile/patient/', views.patient_profile, name='patient_profile'),
    path('profile/doctor/', views.doctor_profile, name='doctor_profile'),

    # Información personal
    path('personal_info/', views.personal_info_view, name='personal_info'),

    # Disponibilidad del doctor
    path('gestionar-disponibilidad/', views.gestionar_disponibilidad, name='gestionar_disponibilidad'),

    # Agendar y gestionar citas
    path('agendar-cita/', views.agendar_cita, name='agendar_cita'),
    path('gestionar-citas/', views.gestionar_citas, name='gestionar_citas'),
    path('confirmar_cita/<int:cita_id>/', views.confirmar_cita, name='confirmar_cita'),

    # Historial y notas del paciente
    path('historial-paciente/<str:username>/', views.ver_historial_paciente, name='ver_historial_paciente'),
    path('agregar-nota/<int:paciente_id>/', views.agregar_nota_paciente, name='agregar_nota_paciente'),
    
    # Elimina la URL que da error, y usa solo la siguiente
    path('ver-notas/', views.ver_notas_paciente, name='ver_notas_paciente'),
    path('editar_nota/<int:nota_id>/', editar_nota, name='editar_nota'),

    # Ver citas
    path('ver-citas/', views.ver_citas_paciente, name='ver_citas_paciente'),
    path('ver-citas-doctor/', views.ver_citas_doctor, name='ver_citas_doctor'),

    # Ingesta de alimentos
    path('food_intake/', views.food_intake_view, name='food_intake'),
    path('patient/<int:patient_id>/food_intake/', views.patient_food_intake_view, name='patient_food_intake'),

    # Listar y ver perfil de doctores
    path('listar_doctores/', views.listar_doctores, name='listar_doctores'),
    path('ver_perfil_doctor/<int:doctor_id>/', views.ver_perfil_doctor, name='ver_doctor'),
    path('elegir_doctor/<int:doctor_id>/', views.elegir_doctor, name='elegir_doctor'),
    path('elegir-paciente/', views.elegir_paciente_para_nota, name='elegir_paciente_para_nota'),
    path('agregar-nota/<int:paciente_id>/', views.agregar_nota_paciente, name='agregar_nota_paciente'),
    path('eliminar-paciente/<int:paciente_id>/', views.eliminar_paciente, name='eliminar_paciente'),
    path('dietas/dia/', views.food_intake_by_day_view, name='food_intake_by_day'),  # Para el paciente
    path('listar_pacientes_sin_asignar/', views.listar_pacientes_sin_asignar, name='listar_pacientes_sin_asignar'),
    path('doctor/dietas/paciente/<int:patient_id>/', views.food_intake_by_day_view, name='doctor_food_intake_by_day'),
    path('asignar_paciente/<int:paciente_id>/', views.asignar_paciente, name='asignar_paciente'),
    path('mis_pacientes/', views.mis_pacientes, name='mis_pacientes'),
    path('test_ai/', views.test_ai_view, name='test_ai'),
    path('test_ai_ingredients/', views.test_ai_view, name='test_ai_ingredients'),
    path('analyze_ingredients/', views.analyze_ingredients_view, name='analyze_ingredients'),



]
