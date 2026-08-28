from django.contrib.auth import logout
from django.shortcuts import redirect

class InactiveUserMiddleware:
    """
    Corta la sesión de usuarios desactivados (por webhook de GH o por la
    administración local). Cierra la ventana de hasta 12h que dejaba la
    sesión activa tras una desactivación.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user is not None and getattr(user, 'is_authenticated', False) and not user.is_active:
            logout(request)
            return redirect('login')
        return self.get_response(request)