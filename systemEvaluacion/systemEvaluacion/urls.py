"""
URL configuration for systemEvaluacion project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
import systemEvaluacion.views as vistas

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='login')),
    path('login', vistas.loguear_usuario),
    path('inicio', vistas.inicio),
    path('registro', vistas.registro_de_usuario),
    path('usuarioTelegram', vistas.ingresar_usuario_telegram),
    path('validarToken', vistas.validar_token_telegram),
    path('logout', vistas.logout),

]
