from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail
import json
import google.generativeai as genai
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os


from .models import PatientProfile

import re
from datetime import datetime

from django.utils import timezone

from django.contrib import messages

import random
import string
from .forms import (
    NotaForm, PatientRegistrationForm, DoctorRegistrationForm, 
    PatientProfileForm, DoctorProfileForm, PersonalInfoForm, 
    DisponibilidadForm, AgendarCitaForm, FoodIntakeForm
)
from .models import (
    DoctorProfile, PatientProfile, Nota, PersonalInfo, 
    DisponibilidadDoctor, Cita, FoodIntake
)

# Contraseña segura: al menos 8 caracteres, una letra mayúscula, una minúscula, un número y un carácter especial
def validar_contrasena(password):
    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
    if not re.search(r'[a-z]', password):
        raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
    if not re.search(r'\d', password):
        raise ValidationError("La contraseña debe contener al menos un número.")
    if not re.search(r'[@$!%*?&]', password):
        raise ValidationError("La contraseña debe contener al menos un carácter especial (@$!%*?&).")

# Validar la longitud máxima de los campos
def validar_longitud_maxima(campo, longitud, nombre_campo):
    if len(campo) > longitud:
        raise ValidationError(f"{nombre_campo} no debe exceder los {longitud} caracteres.")

# Validación del correo electrónico
def validar_correo_electronico(email):
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError("Ingrese un correo electrónico válido.")

# Vista para la página principal
def home(request):
    return render(request, 'nutrition/home.html')

# Registro para pacientes
def register_patient(request):
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Validar nombre de usuario (máximo 150 caracteres)
            validar_longitud_maxima(username, 150, 'Nombre de usuario')

            # Validar correo electrónico
            validar_correo_electronico(email)

            # Validar contraseña segura
            try:
                validar_contrasena(password)
            except ValidationError as e:
                form.add_error('password', e.message)

            # Validar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Este nombre de usuario ya está en uso.')
            elif User.objects.filter(email=email).exists():
                form.add_error('email', 'Este correo electrónico ya está en uso.')
            else:
                # Crear el usuario y el perfil de paciente si no hay errores
                user = User.objects.create_user(username=username, email=email, password=password)
                PatientProfile.objects.create(user=user)
                return redirect('registration_successful')
    else:
        form = PatientRegistrationForm()
    return render(request, 'nutrition/register_patient.html', {'form': form})

# Registro para doctores
def register_doctor(request):
    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Validar nombre de usuario (máximo 150 caracteres)
            validar_longitud_maxima(username, 150, 'Nombre de usuario')

            # Validar correo electrónico
            validar_correo_electronico(email)

            # Validar contraseña segura
            try:
                validar_contrasena(password)
            except ValidationError as e:
                form.add_error('password', e.message)

            # Validar si el usuario ya existe
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'Este nombre de usuario ya está en uso.')
            elif User.objects.filter(email=email).exists():
                form.add_error('email', 'Este correo electrónico ya está en uso.')
            else:
                # Crear el usuario y el perfil de doctor
                user = User.objects.create_user(username=username, email=email, password=password)
                DoctorProfile.objects.create(user=user, doctor_id=''.join(random.choices(string.ascii_uppercase + string.digits, k=10)))
                return redirect('registration_successful')
    else:
        form = DoctorRegistrationForm()
    return render(request, 'nutrition/register_doctor.html', {'form': form})

# Login para pacientes
def patient_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Validar que los campos no estén vacíos
            if not username or not password:
                form.add_error(None, 'Debe proporcionar un nombre de usuario y una contraseña.')
            else:
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('patient_home')
                else:
                    form.add_error(None, 'Credenciales inválidas.')
    else:
        form = AuthenticationForm()
    return render(request, 'nutrition/patient_login.html', {'form': form})

# Login para doctores
def doctor_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # Validar que los campos no estén vacíos
            if not username or not password:
                form.add_error(None, 'Debe proporcionar un nombre de usuario y una contraseña.')
            else:
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('doctor_home')
                else:
                    form.add_error(None, 'Credenciales inválidas.')
    else:
        form = AuthenticationForm()
    return render(request, 'nutrition/doctor_login.html', {'form': form})

# Vista para el home de los doctores
@login_required
def doctor_home(request):
    # Obtener todos los pacientes asignados a este doctor
    patients = PatientProfile.objects.filter(doctor=request.user)

    # Obtener las citas pendientes del doctor
    citas_pendientes = Cita.objects.filter(doctor=request.user, estado='Pendiente')

    return render(request, 'nutrition/doctor_home.html', {
        'user': request.user,
        'patients': patients,
        'citas_pendientes': citas_pendientes,
    })

# Perfil del doctor
@login_required
def doctor_profile(request):
    # Verificar si el usuario tiene un perfil de doctor, si no, lo crea
    if not hasattr(request.user, 'doctorprofile'):
        DoctorProfile.objects.create(user=request.user)

    doctor_profile = request.user.doctorprofile

    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=doctor_profile)
        if form.is_valid():
            form.save()
            return redirect('doctor_profile')
    else:
        form = DoctorProfileForm(instance=doctor_profile)

    return render(request, 'nutrition/doctor_profile.html', {'form': form})

# Vista para el home de los pacientes
@login_required
def patient_home(request):
    return render(request, 'nutrition/patient_home.html')

# Perfil del paciente
@login_required
def patient_profile(request):
    if not hasattr(request.user, 'patientprofile'):
        PatientProfile.objects.create(user=request.user)

    patient_profile = request.user.patientprofile

    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=patient_profile)
        if form.is_valid():
            form.save()
            return redirect('patient_profile')
    else:
        form = PatientProfileForm(instance=patient_profile)

    return render(request, 'nutrition/patient_profile.html', {'form': form})

# Vista de éxito después del registro
def registration_successful(request):
    return render(request, 'nutrition/registration_successful.html')

# Restablecer la contraseña
reset_codes = {}

def generate_reset_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def request_password_reset(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        try:
            # Validar formato de correo electrónico
            validar_correo_electronico(email)
            user = User.objects.get(username=username, email=email)
            reset_code = generate_reset_code()
            reset_codes[username] = reset_code
            return render(request, 'nutrition/password_reset_code.html', {'reset_code': reset_code})
        except User.DoesNotExist:
            return render(request, 'nutrition/password_reset_request.html', {'error': 'Usuario o correo electrónico incorrectos'})
    return render(request, 'nutrition/password_reset_request.html')

def password_reset_confirm(request):
    if request.method == 'POST':
        username = request.POST['username']
        code = request.POST['code']
        new_password = request.POST['new_password']

        # Validar contraseña
        try:
            validar_contrasena(new_password)
        except ValidationError as e:
            return render(request, 'nutrition/password_reset_confirm.html', {'error': e.message})

        if username in reset_codes and reset_codes[username] == code:
            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                del reset_codes[username]
                return redirect('password_reset_complete')
            except User.DoesNotExist:
                return render(request, 'nutrition/password_reset_confirm.html', {'error': 'Usuario no encontrado'})
        else:
            return render(request, 'nutrition/password_reset_confirm.html', {'error': 'Código incorrecto o expirado'})
    return render(request, 'nutrition/password_reset_confirm.html')

def password_reset_complete(request):
    return render(request, 'nutrition/password_reset_complete.html')

@login_required
def personal_info_view(request):
    try:
        # Si el usuario no tiene un personal_info asociado, lo creamos
        personal_info, created = PersonalInfo.objects.get_or_create(user=request.user)
    except PersonalInfo.DoesNotExist:
        personal_info = None

    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, instance=personal_info)
        
        # Validaciones personalizadas
        if not form.is_valid():
            error_message = 'Hay errores en los datos ingresados. Verifique los campos.'
            return render(request, 'nutrition/personal_info.html', {'form': form, 'error': error_message})

        # Validar datos manualmente si se requiere (ejemplo de validación personalizada)
        try:
            personal_info = form.save(commit=False)

            # Validación personalizada de la longitud de la CURP
            if len(personal_info.curp) != 18:
                raise ValidationError("La CURP debe tener 18 caracteres.")

            # Se pueden agregar más validaciones si es necesario

            personal_info.user = request.user
            personal_info.save()
            return redirect('personal_info')  # Cambiar según tu ruta

        except ValidationError as e:
            return render(request, 'nutrition/personal_info.html', {'form': form, 'error': str(e)})
        
    else:
        form = PersonalInfoForm(instance=personal_info)

    return render(request, 'nutrition/personal_info.html', {'form': form})

@login_required
def gestionar_disponibilidad(request):
    if not request.user.groups.filter(name='Doctores').exists():  # Solo los doctores pueden acceder
        return redirect('home')

    if request.method == 'POST':
        form = DisponibilidadForm(request.POST)
        if form.is_valid():
            disponibilidad = form.save(commit=False)
            disponibilidad.doctor = request.user
            disponibilidad.save()
            return redirect('gestionar_disponibilidad')
    else:
        form = DisponibilidadForm()
    
    disponibilidad_doctor = DisponibilidadDoctor.objects.filter(doctor=request.user)
    return render(request, 'nutrition/gestionar_disponibilidad.html',
                   {'form': form, 'disponibilidad_doctor': disponibilidad_doctor})
@login_required
def agendar_cita(request):
    if request.method == 'POST':
        form = AgendarCitaForm(request.POST)
        if form.is_valid():
            cita = form.save(commit=False)
            cita.paciente = request.user  # El paciente es el usuario logueado
            cita.save()

            # Asignar el doctor al perfil del paciente si no tiene uno asignado
            patient_profile = request.user.patientprofile
            if patient_profile.doctor is None:  # Verificar si el paciente ya tiene un doctor
                patient_profile.doctor = cita.doctor  # Asignar el doctor de la cita
                patient_profile.save()

            return redirect('ver_citas_paciente')
    else:
        form = AgendarCitaForm()
    
    return render(request, 'nutrition/agendar_cita.html', {'form': form})



@login_required
def gestionar_citas(request):
    citas = Cita.objects.filter(doctor=request.user)
    if request.method == 'POST':
        cita_id = request.POST.get('cita_id')
        accion = request.POST.get('accion')
        cita = Cita.objects.get(id=cita_id)
        if accion == 'confirmar':
            cita.estado = 'Confirmada'
        elif accion == 'rechazar':
            cita.estado = 'Rechazada'
        cita.save()
        return redirect('gestionar_citas')

    return render(request, 'nutrition/gestionar_citas.html', {'citas': citas})






@login_required
def gestionar_citas(request):
    citas = Cita.objects.filter(doctor=request.user)
    if request.method == 'POST':
        cita_id = request.POST.get('cita_id')
        accion = request.POST.get('accion')
        cita = Cita.objects.get(id=cita_id)
        if accion == 'confirmar':
            cita.estado = 'Confirmada'
            send_mail(
                'Confirmación de Cita',
                f'Su cita con el Dr. {cita.doctor.username} ha sido confirmada.',
                'from@example.com',
                [cita.paciente.email],
                fail_silently=False,
            )
        elif accion == 'rechazar':
            cita.estado = 'Rechazada'
            send_mail(
                'Rechazo de Cita',
                f'Su cita con el Dr. {cita.doctor.username} ha sido rechazada.',
                'from@example.com',
                [cita.paciente.email],
                fail_silently=False,
            )
        cita.save()
        return redirect('gestionar_citas')

    return render(request, 'nutrition/gestionar_citas.html', {'citas': citas})

@login_required
def ver_historial_paciente(request, username):
    # Buscar al paciente por su username
    paciente = get_object_or_404(User, username=username)
    
    # Obtener el perfil del paciente basado en el usuario encontrado
    patient_profile = get_object_or_404(PatientProfile, user=paciente)

    # Verificar que el doctor esté asignado a este paciente
    if patient_profile.doctor != request.user:
        return redirect('home')  # Redirigir si no es el doctor asignado

    # Obtener las notas del doctor relacionadas con este paciente
    notas = Nota.objects.filter(paciente=paciente, doctor=request.user)

    # Renderizar la plantilla con los datos del paciente y las notas
    return render(request, 'nutrition/ver_historial_paciente.html', {
        'paciente': paciente,
        'patient_profile': patient_profile,
        'notas': notas,
    })




@login_required
def ver_notas_paciente(request):
    # Asegurarse de que sea un paciente
    if not hasattr(request.user, 'patientprofile'):
        return redirect('home')  # Redirigir si no es paciente

    notas = Nota.objects.filter(paciente=request.user)

    return render(request, 'nutrition/ver_notas_paciente.html', {'notas': notas})

##############################################################################

@login_required
def editar_nota(request, nota_id):
    nota = get_object_or_404(Nota, id=nota_id, doctor=request.user)
    if request.method == 'POST':
        form = NotaForm(request.POST, instance=nota)
        if form.is_valid():
            form.save()
            return redirect('ver_notas_paciente')  # Redirige a la lista de notas del paciente
    else:
        form = NotaForm(instance=nota)
    return render(request, 'nutrition/editar_nota.html', {'form': form})

##############################################################################



@login_required
def ver_citas_paciente(request):
    citas = Cita.objects.filter(paciente=request.user)
    return render(request, 'nutrition/ver_citas_paciente.html', {'citas': citas})

@login_required
def ver_citas_doctor(request):    
    citas = Cita.objects.filter(doctor=request.user)
    return render(request, 'nutrition/ver_citas_doctor.html', {'citas': citas})

@login_required
def food_intake_view(request):
    # Verificar si se envió un formulario por método POST
    if request.method == 'POST':
        form = FoodIntakeForm(request.POST)
        if form.is_valid():
            # Crear el registro de alimentos sin guardarlo aún
            food_intake = form.save(commit=False)
            # Asignar el usuario que está registrando el alimento
            food_intake.user = request.user
            # Guardar el registro en la base de datos
            food_intake.save()
            # Redirigir a la misma página después de guardar el alimento
            return redirect('food_intake')
    else:
        form = FoodIntakeForm()
    
    # Obtener todos los alimentos registrados por el usuario actual
    food_intakes = FoodIntake.objects.filter(user=request.user).order_by('-date', '-time')
    
    return render(request, 'nutrition/food_intake.html', {'form': form, 'food_intakes': food_intakes})

@login_required
def patient_food_intake_view(request, patient_id):
    food_intakes = FoodIntake.objects.filter(user_id=patient_id).order_by('-date', '-time')
    return render(request, 'nutrition/patient_food_intake.html', {'food_intakes': food_intakes})
from datetime import datetime
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from .models import FoodIntake, User
@login_required
def food_intake_by_day_view(request, patient_id=None):
    # Si el doctor está viendo, utilizamos el ID del paciente, si no, es el propio paciente viendo su comida
    if patient_id:
        patient = get_object_or_404(User, id=patient_id)
    else:
        patient = request.user

    # Filtrar por la fecha seleccionada o usar la fecha actual si no hay selección
    date_str = request.GET.get('date')
    if date_str:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        selected_date = timezone.now().date()

    # Obtener los alimentos registrados en esa fecha
    food_intakes = FoodIntake.objects.filter(user=patient, date=selected_date)

    # Obtener los platillos analizados por el paciente
    dish_analyses = FoodAnalysis.objects.filter(user=patient)

    # Obtener los ingredientes analizados por el paciente
    ingredient_analyses = IngredientAnalysis.objects.filter(user=patient)

    context = {
        'food_intakes': food_intakes,
        'selected_date': selected_date,
        'patient': patient,
        'is_doctor_viewing': patient_id is not None,
        'dish_analyses': dish_analyses,
        'ingredient_analyses': ingredient_analyses,
    }

    return render(request, 'nutrition/food_intake_by_day.html', context)

@login_required
def confirmar_cita(request, cita_id):
    cita = get_object_or_404(Cita, id=cita_id)
    if request.method == 'POST':
        cita.estado = 'Confirmada'
        cita.save()
        send_mail(
            'Confirmación de Cita',
            f'Su cita con el Dr. {cita.doctor.username} ha sido confirmada.',
            'from@example.com',
            [cita.paciente.email],
            fail_silently=False,
        )
        return redirect('gestionar_citas')
    return render(request, 'nutrition/confirmar_cita.html', {'cita': cita})




@login_required
def listar_doctores(request):
    doctores = DoctorProfile.objects.all()
    return render(request, 'nutrition/listar_doctores.html', {'doctores': doctores})



@login_required
def ver_perfil_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    return render(request, 'nutrition/ver_doctor.html', {'doctor': doctor})




@login_required
def elegir_doctor(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, id=doctor_id)
    patient_profile = request.user.patientprofile
    patient_profile.doctor = doctor.user
    patient_profile.save()
    return redirect('patient_home')

@login_required
def elegir_paciente_para_nota(request):
    pacientes = PatientProfile.objects.all()  # Obtén todos los pacientes
    return render(request, 'nutrition/elegir_paciente_para_nota.html', {'pacientes': pacientes})

# Vista para agregar una nota a un paciente
@login_required
def agregar_nota_paciente(request, paciente_id):
    paciente = get_object_or_404(PatientProfile, user_id=paciente_id)
    
    # Obtener todas las notas que el doctor ha dejado para este paciente
    notas_previas = Nota.objects.filter(paciente=paciente.user, doctor=request.user)
    
    if request.method == 'POST':
        form = NotaForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.paciente = paciente.user
            nota.doctor = request.user
            nota.save()
            return redirect('doctor_home')  # Redirige a la página principal del doctor después de guardar la nota
    else:
        form = NotaForm()

    return render(request, 'nutrition/agregar_nota_paciente.html', {
        'form': form,
        'paciente': paciente,
        'notas_previas': notas_previas,  # Pasar las notas previas al contexto
    })
@login_required
def eliminar_paciente(request, paciente_id):
    paciente = get_object_or_404(PatientProfile, user_id=paciente_id)

    if request.method == 'POST':
        paciente.user.delete()  # Elimina el usuario asociado al paciente
        messages.success(request, f'El paciente {paciente.user.username} ha sido eliminado exitosamente.')
        return redirect('elegir_paciente_para_nota')

    return render(request, 'nutrition/eliminar_paciente_confirmacion.html', {'paciente': paciente})

from django.shortcuts import get_object_or_404, redirect

@login_required
def listar_pacientes_sin_asignar(request):
    # Obtener todos los pacientes que no tienen un doctor asignado
    pacientes_sin_doctor = PatientProfile.objects.filter(doctor__isnull=True)
    
    return render(request, 'listar_pacientes_sin_asignar.html', {'pacientes_sin_doctor': pacientes_sin_doctor})

@login_required
def asignar_paciente(request, paciente_id):
    # Obtener el perfil del paciente
    paciente = get_object_or_404(PatientProfile, id=paciente_id)
    # Asignar el paciente al doctor logueado
    paciente.doctor = request.user
    paciente.save()

    # Redirigir a la vista de "Mis Pacientes"
    return redirect('mis_pacientes')

@login_required
def mis_pacientes(request):
    # Obtener todos los pacientes que tienen al doctor logueado asignado
    pacientes = PatientProfile.objects.filter(doctor=request.user)

    return render(request, 'mis_pacientes.html', {'pacientes': pacientes})


# Configurar la API de Google Gemini
def model_configai():
    genai.configure(api_key="AIzaSyDqda00j5UESUeKrFIxLtRAzoIIE1hW3vA")

    generation_config = {
        "temperature": 1,
        "top_k": 64,
        "top_p": 0.95,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
        }
    
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    return model

def upload_to_gemini(path, mime_type=None):
 
  file = genai.upload_file(path, mime_type=mime_type)
  print(f"Uploaded file '{file.display_name}' as: {file.uri}")
  return file

def lim_prompt_egineering_image(model, image_path):
    files = [upload_to_gemini(image_path, mime_type="image/jpeg")]
    chat = model.start_chat(
        history = [
            {"role":"user",
            "parts": '''Hola, vas a recibir una imagen y vas a jugar el rol de nutriólogo. 
            El objetivo es analizar el plato de comida que te voy a enviar y analizar lo siguiente:
            - Número de calorías aproximado
            - Ingredientes del plato
            - Si consideras que el plato es sano o no.
            El resultado de todo esto me lo vas a devolver en un JSON.'''
            },
        ]
    )

    response = chat.send_message("Aquí va la imagen")
    return response.text


# Función para subir la imagen a Gemini
def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

# Función para realizar el análisis nutricional de la imagen
def lim_prompt_engineering_image(model, image_path):
    files = [upload_to_gemini(image_path, mime_type="image/jpeg")]
    chat = model.start_chat(
        history = [
            {"role": "user",
             "parts": '''Hola, vas a recibir una imagen y vas a jugar el rol de nutriólogo. 
             El objetivo es analizar el plato de comida que te voy a enviar y analizar lo siguiente:
             - Número de calorías aproximado
             - Ingredientes del plato
             - Si consideras que el plato es sano o no.
             El resultado de todo esto me lo vas a devolver en un JSON.'''
            },
        ]
    )

    response = chat.send_message("Aquí va la imagen")
    return response.text

# Vista para subir y analizar imágenes con el modelo configurado de IA
@login_required
def upload_and_analyze_image(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Guardar la imagen subida
            uploaded_image = request.FILES['image']
            fs = FileSystemStorage()
            filename = fs.save(uploaded_image.name, uploaded_image)
            uploaded_file_url = fs.url(filename)

            # Obtener el modelo configurado
            model = model_configai()
            
            # Procesar la imagen y obtener el análisis
            try:
                image_path = os.path.join(settings.MEDIA_ROOT, filename)
                analysis_result = lim_prompt_engineering_image(model, image_path)
                
                return render(request, 'nutrition/analyze_result.html', {
                    'uploaded_file_url': uploaded_file_url,
                    'analysis_result': analysis_result
                })
            except Exception as e:
                messages.error(request, f"Error al analizar la imagen: {str(e)}")
    
    else:
        form = ImageUploadForm()

    return render(request, 'nutrition/upload_image.html', {'form': form})
import google.generativeai as genai
import time


def model_configai():
    genai.configure(api_key="AIzaSyDqda00j5UESUeKrFIxLtRAzoIIE1hW3vA")

    generation_config = {
        "temperature": 1,
        "top_k": 64,
        "top_p": 0.95,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
        }
    
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)
    return model



def upload_to_gemini(path, mime_type=None):
    file = genai.upload_file(path, mime_type=mime_type)
    return file

import logging

def analyze_food_image(image_path):
    try:
        model = model_configai()
        file = upload_to_gemini(image_path, mime_type="image/jpeg")
        logging.debug(f"File uploaded: {file}")
        
        chat = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        file,
                        '''
                        Hola, vas a recibir una imagen y vas a jugar el rol de nutriólogo.
                        Tu tarea es analizar el plato de comida en la imagen y proporcionar la siguiente información en formato JSON:
                        1. "calorias": el número aproximado de calorías del plato.
                        2. "ingredientes": una lista de los ingredientes principales del plato.
                        3. "es_sano": un booleano que indique si consideras que el plato es saludable (true) o no (false).
                        porfavor,asegúrate de que el JSON esté bien estructurado y que las claves sean exactamente como se especifica.
                        '''
                    ],
                }
            ]
        )
        response = chat.send_message("aqui va la imagen")
        logging.debug(f"Response received: {response}")

        
        return response
    except Exception as e:
        logging.error(f"Error in analyze_food_image: {e}")
        return None






# Vista de prueba para la IA
from django.http import HttpResponse
from .models import IngredientAnalysis

from .models import FoodAnalysis

def test_ai_view(request):
    analyses = FoodAnalysis.objects.filter(user=request.user)  # Obtener los análisis previos del usuario

    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        with open('temp_image.jpg', 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        
        try:
            analysis_result = analyze_food_image('temp_image.jpg')
            
            # Acceder al contenido JSON dentro de la respuesta
            raw_content = analysis_result.candidates[0].content.parts[0].text
            content_json = raw_content.replace("```json", "").replace("```", "")
            content_dict = json.loads(content_json)

            # Guardar los datos en el modelo
            FoodAnalysis.objects.create(
                user=request.user,
                calorias=content_dict["calorias"],
                ingredientes=", ".join(content_dict["ingredientes"]),  # Convertir lista a string
                es_sano=content_dict["es_sano"]
            )

            # Formatear el JSON para mostrarlo bonito
            formatted_json = json.dumps(content_dict, indent=4)

            return render(request, 'nutrition/test_ai.html', {
                'formatted_json': formatted_json,
                'analyses': analyses  # Pasar los análisis al contexto
            })
        except Exception as e:
            logging.error(f"Error al analizar la imagen: {e}")
            return HttpResponse(f"Error al analizar la imagen: {e}")
    return render(request, 'nutrition/test_ai.html', {'analyses': analyses})

def analyze_ingredients_image(image_path):
    try:
        model = model_configai()  # Usa tu función para configurar el modelo de IA
        file = upload_to_gemini(image_path, mime_type="image/jpeg")
        logging.debug(f"File uploaded: {file}")
        
        chat = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        file,
                        '''
                        Hola, vas a recibir una imagen con ingredientes crudos.
                        Tu tarea es analizar los ingredientes en la imagen y proporcionar la siguiente información en formato JSON:
                        1. "ingredientes": una lista de los ingredientes principales presentes en la imagen.
                        2. "recomendacion": una recomendación de un platillo que se pueda preparar con estos ingredientes.
                        Asegúrate de que el JSON esté bien estructurado y que las claves sean exactamente como se especifica.
                        '''
                    ],
                }
            ]
        )
        response = chat.send_message("Aquí va la imagen")
        logging.debug(f"Response received: {response}")
        return response
    except Exception as e:
        logging.error(f"Error in analyze_ingredients_image: {e}")
        return None

def analyze_ingredients_view(request):
    analyses = IngredientAnalysis.objects.filter(user=request.user)  # Obtener los análisis previos del usuario

    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        with open('temp_ingredients_image.jpg', 'wb+') as destination:
            for chunk in image.chunks():
                destination.write(chunk)
        
        try:
            analysis_result = analyze_ingredients_image('temp_ingredients_image.jpg')
            
            # Acceder al contenido JSON dentro de la respuesta
            raw_content = analysis_result.candidates[0].content.parts[0].text
            content_json = raw_content.replace("```json", "").replace("```", "")
            content_dict = json.loads(content_json)

            # Guardar los datos en el modelo IngredientAnalysis
            IngredientAnalysis.objects.create(
                user=request.user,
                ingredientes=", ".join(content_dict["ingredientes"]),  # Convertir lista a string
                recomendacion=content_dict["recomendacion"]
            )

            # Formatear el JSON para mostrarlo bonito
            formatted_json = json.dumps(content_dict, indent=4)

            return render(request, 'nutrition/analyze_ingredients.html', {
                'formatted_json': formatted_json,
                'analyses': analyses  # Pasar los análisis al contexto
            })
        except Exception as e:
            logging.error(f"Error al analizar la imagen: {e}")
            return HttpResponse(f"Error al analizar la imagen: {e}")
    
    return render(request, 'nutrition/analyze_ingredients.html', {'analyses': analyses})