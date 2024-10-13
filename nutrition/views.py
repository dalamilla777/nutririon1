from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail
import re
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
    doctor_profile = request.user.doctorprofile
    patients = PatientProfile.objects.filter(doctor=request.user)
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
            cita.paciente = request.user
            cita.save()
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
def ver_historial_paciente(request, paciente_id):
    paciente = User.objects.get(id=paciente_id)
    notas = Nota.objects.filter(paciente=paciente, doctor=request.user)
    return render(request, 'nutrition/ver_historial_paciente.html', {'paciente': paciente, 'notas': notas})

@login_required
def agregar_nota_paciente(request, paciente_id):
    paciente = User.objects.get(id=paciente_id)
    if request.method == 'POST':
        form = NotaForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.paciente = paciente
            nota.doctor = request.user
            nota.save()
            return redirect('ver_historial_paciente', paciente_id=paciente_id)
    else:
        form = NotaForm()
    return render(request, 'nutrition/agregar_nota_paciente.html', {'form': form, 'paciente': paciente})

@login_required
def ver_notas(request, paciente_id):
    paciente = get_object_or_404(PatientProfile, user_id=paciente_id)
    notas = Nota.objects.filter(paciente=paciente)
    
    return render(request, 'nutrition/ver_notas.html', {
        'paciente': paciente,
        'notas': notas,
    })

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
    if request.method == 'POST':
        form = FoodIntakeForm(request.POST)
        if form.is_valid():
            food_intake = form.save(commit=False)
            food_intake.user = request.user
            food_intake.save()
            return redirect('food_intake')  # Cambiar según tu ruta
    else:
        form = FoodIntakeForm()
    
    return render(request, 'nutrition/food_intake.html', {'form': form})

@login_required
def patient_food_intake_view(request, patient_id):
    food_intakes = FoodIntake.objects.filter(user_id=patient_id).order_by('-date', '-time')
    return render(request, 'nutrition/patient_food_intake.html', {'food_intakes': food_intakes})

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

