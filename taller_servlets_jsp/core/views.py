from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages

def home(request):
    if request == "get":
        return render(request, "home.html")
    else:
        return render(request, "home.html")

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/inventario/')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Bienvenido, {user.get_full_name() or user.username}.')
            return redirect(request.POST.get('next') or '/inventario/')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'login.html')

def logout_view(request):
    nombre = request.user.get_full_name() or request.user.username
    logout(request)
    messages.success(request, f'Sesión cerrada correctamente. ¡Hasta pronto, {nombre}!')
    return redirect('login')