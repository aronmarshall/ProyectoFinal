from pyexpat.errors import messages
from urllib import request
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from datetime import datetime
from datetime import timezone


from bd import models
from systemEvaluacion import settings
from api import telegram

import os
import base64
import crypt
import requests
import re

def inicio(request):
    """_summary_
    Renderiza la página de inicio.

    Esta vista maneja las solicitudes a la página de inicio de la aplicación.
    Utiliza la función render de Django para devolver la plantilla 'inicio.html'.

    Args:
        request: Objeto HttpRequest que contiene los datos de la solicitud.

    Returns:
        HttpResponse: La respuesta HTTP con el contenido renderizado de la plantilla 'inicio.html'.
    """
    return render(request, 'inicio.html')

def registro_de_usuario(request):
    
    if request.method == 'POST':
        nombre_completo = request.POST.get('nombre_completo')
        matricula = request.POST.get('matricula')
        usuario = request.POST.get('usuario_nuevo')
        contrasenia = request.POST.get('contrasenia')
        contrasenia_confirma = request.POST.get('contrasenia_confirma')

        existe_usuario_registrado = models.Usuario.objects.filter(usuario=usuario).exists()
        if existe_usuario_registrado :
            messages.info(request, f'Lo siento, el usuario {usuario} esta en uso.')
            return render(request, 'registro.html')
        else:
            if contrasenia == contrasenia_confirma:
                if politica_de_contrasenia(contrasenia):
                    salt_generado=generador_de_salt()
                    hasheado = crypt.crypt(contrasenia, '$6$' + salt_generado)
                    nuevo_alumno = models.Alumno(nombre_completo=nombre_completo, matricula=matricula)
                    nuevo_alumno.save()
                    id_alumno = nuevo_alumno.id
                    nuevo_usuario = models.Usuario(usuario=usuario, contrasenia=hasheado.encode(), alumno_id=id_alumno)
                    nuevo_usuario.save()
                    messages.success(request, f'Se realizó la operación de manera correcta. {usuario}')
                    return render(request, 'registro.html')
                else:
                    messages.error(request, 'La contraseña no cumple con las políticas.')
                    return render(request, 'registro.html')
            else:
                messages.error(request, 'Las contraseñas no son iguales.')
                return render(request, 'registro.html')
    return render(request, 'registro.html')

def politica_de_contrasenia(contrasenia):
    pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{10,}$')
    return pattern.match(contrasenia)

def generador_de_salt():
    while True:
        valor_aleatorio = os.urandom(16)
        valor_generado_salt = base64.b64encode(valor_aleatorio).decode('utf-8')
        existe_salt_generado = models.TokenOcupados.objects.filter(token=valor_generado_salt).exists()
        if not existe_salt_generado:
            salt_guardado = models.TokenOcupados(token=valor_generado_salt)
            salt_guardado.save()
            break
    return valor_generado_salt
################################################################
def loguear_usuario(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        usuario = request.POST.get('login_usuario')
        contrasenia = request.POST.get('login_contrasenia')

        if not usuario or not contrasenia:
            messages.info(request, "Completa ambos campos.")
            return render(request, 'login.html')
        
        else:
            existe_usuario = models.Usuario.objects.filter(usuario=usuario).exists()
            if not existe_usuario:
                messages.error(request, "Usuario o contraseña incorrectos")
                return render(request, 'login.html')
            else:
                if consultar_hash(usuario, contrasenia):
                    
                    return HttpResponseRedirect('autenticacion')
                else:
                    messages.error(request, "Usuario o contraseña incorrectos")
                    return render(request, 'login.html')
    else:
        return render(request, 'login.html')

def consultar_hash(usuario:str, contrasenia:str): 

    usuario = models.Usuario.objects.filter(usuario=usuario).first()
    hasheado = usuario.contrasenia.decode('utf-8')
    partes = hasheado.split('$')
    complemento = '$' + partes[1] + '$' + partes[2]
    if hasheado == crypt.crypt(contrasenia, complemento):
        return True
    else:
        return False

############################################################

def doble_factor(request):
    if request.method == 'GET':
        return render(request, 'autenticacion.html')
    elif request.method == 'POST':
        usuario_telegram = request.POST.get('usuario_telegram')
        if telegram.procesar_doble_factor(usuario_telegram):
            return HttpResponseRedirect('validarToken')
        else:
            return HttpResponseRedirect('enviarMensaje')
##################################################################
def redirigir_a_mensaje(request):
    return render(request, 'enviarMensaje.html')
##################################################################


def validar_token_telegram(request):
    if request.method == 'GET':
        return render(request, 'validarToken.html')
    elif request.method == 'POST':
        caracter1 = request.POST.get('c1')
        caracter2 = request.POST.get('c2')
        caracter3 = request.POST.get('c3')
        caracter4 = request.POST.get('c4')
        caracter5 = request.POST.get('c5')
        caracter6 = request.POST.get('c6')

        token_ingresado = caracter1 + caracter2 + caracter3 + caracter4 + caracter5 + caracter6
        
        if verificar_token_ingresado(token_ingresado) :
            return render(request, 'inicio.html')
        else:
            messages.error(request, f'Lo siento, el token {token_ingresado} ya no es válido')
            return render(request, 'login.html')

    
def verificar_token_ingresado(token_ingresado):
    existe_token = models.validaToken.objects.filter(tokens=token_ingresado).first()
    if existe_token:
        if existe_token.tokens == token_ingresado:
            return True
        else:
            return False
    else: 
        return False