from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required
from .models import Usuario
from .forms import FormUsuario, LoginForm
from django.core.exceptions import PermissionDenied
from django.contrib import messages

def loginUsuario(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            try:
                # Intentar obtener el usuario por email
                user = Usuario.objects.get(email=email)
                # Autenticar usando el email como username
                auth_user = authenticate(request, username=email, password=password)
                if auth_user is not None:
                    login(request, auth_user)
                    messages.success(request, f'Bienvenido {auth_user.first_name}!')
                    next_url = request.GET.get('next', '/')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Contraseña incorrecta')
            except Usuario.DoesNotExist:
                messages.error(request, 'No existe un usuario con ese email')
    else:
        form = LoginForm()
    return render(request, 'UsuariosApp/Login.html', {'form': form})


def logoutUsuario(request):
    """
    Se crea la vista para cerrar sesión.
    """
    logout(request)
    return redirect('/')

@login_required
def listado_usuarios(request):
    try:
        if not request.user.is_authenticated:
            return redirect(loginUsuario)
        
        usuarios = Usuario.objects.all()
        
        try:
            usuario_actual = Usuario.objects.get(email=request.user.email)
            show_passwords = usuario_actual.role == 'Gerente' or request.user.is_superuser
        except Usuario.DoesNotExist:
            show_passwords = request.user.is_superuser
            
        data = {
            'usuarios': usuarios,
            'show_passwords': show_passwords,
            'is_admin': request.user.is_superuser,
            'user_role': usuario_actual.role,  # Añadimos el rol del usuario actual
            'user_name': request.user.first_name  # Añadimos el nombre del usuario actual
        }
        return render(request, 'UsuariosApp/ListadoUsuarios.html', data)
    except PermissionDenied:
        messages.warning(request, 'No tienes permisos para acceder a esta página.')
        return render(request, 'UsuariosApp/ListadoUsuarios.html')


def registrar_usuario(request):
    if request.method == 'POST':
        form = FormUsuario(request.POST)
        if form.is_valid():
            try:
                if form.cleaned_data['password1'] != form.cleaned_data['password2']:
                    messages.error(request, 'Las contraseñas no coinciden')
                    return render(request, 'UsuariosApp/RegistrarUsuario.html', {'form': form})

                usuario = Usuario.objects.create_user(
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password1'],
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    role=form.cleaned_data['role'],
                    rut=form.cleaned_data['rut']
                )
                messages.success(request, 'Usuario registrado correctamente')
                return redirect('listado')
            except Exception as e:
                messages.error(request, f'Error al registrar: {str(e)}')
    else:
        form = FormUsuario()
    
    return render(request, 'UsuariosApp/RegistrarUsuario.html', {'form': form})


    
@login_required
def eliminar_usuario(request, id):
    """
    Se crea la vista para eliminar un usuario.
    Se obtiene el usuario a eliminar y se elimina de la base de datos.
    Se redirige a la lista de usuarios.
    """
    usuario = Usuario.objects.get(id=id)
    usuario.delete()
    return redirect(listado_usuarios)

@login_required 
def actualizar_usuario(request, id):
    """
    Se crea la vista para actualizar un usuario.
    Se obtiene el usuario a actualizar y se crea un formulario con los datos del usuario.
    Si el formulario es válido, se actualiza el usuario y se redirige a la lista de usuarios.
    """
    usuario = Usuario.objects.get(id=id)
    form = FormUsuario(instance=usuario)
    if request.method == 'POST':
        form = FormUsuario(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return listado_usuarios(request)
    data = {'form': form}
    return render(request,'UsuariosApp/RegistrarUsuario.html', data)
