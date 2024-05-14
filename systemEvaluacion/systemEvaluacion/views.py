from pyexpat.errors import messages
from urllib import request
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from datetime import datetime
from datetime import timezone

import requests
from bd import models
from systemEvaluacion import settings
import os
import base64
import crypt


TOKEN = '7199611399:AAHrE8s0MW6oLz-MmhI6RzFDs-TCFaxq7q8'  
URL = f'https://api.telegram.org/bot{TOKEN}/getUpdates'


def inicio(request):
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
                messages.error(request, 'Las contraseñas no son iguales.')
                return render(request, 'registro.html')
    return render(request, 'registro.html')

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
        procesar_doble_factor(usuario_telegram)
        #return render(request, 'validarToken.html')
        return HttpResponseRedirect('validarToken')

def procesar_doble_factor(usuario_telegram):
    try:
        chat_id = obtener_chat_id(usuario_telegram)
        if chat_id:
            token = generar_token()
            tiempo = obtener_tiempo()
            guardar_token = models.validaToken(tokens=token, tiempo=tiempo)
            guardar_token.save()
            enviar_mensaje_telegram(chat_id, f'Hola usuario tu Token es: {token}')
        else:
            messages.info(request, f'El usuario {usuario_telegram} no ha enviado mensajes al bot.')
    except requests.exceptions.HTTPError as e:
        messages.error(request, f'Error al realizar la solicitud HTTP: {e}')
    except Exception as ex:
        messages.error(request, f'Error inesperado: {ex}')

def obtener_chat_id(usuario_telegram):
    URL = 'https://api.telegram.org/bot{}/getUpdates'.format(TOKEN)
    response = requests.get(URL)
    response.raise_for_status()
    data = response.json()
    for update in data['result']:
        if 'message' in update and 'chat' in update['message'] and 'username' in update['message']['chat']:
            if update['message']['chat']['username'] == usuario_telegram:
                return update['message']['chat']['id']
    return None
def obtener_tiempo():
    tiempo = datetime.now()
    tiempo_actual = tiempo.strftime('%H:%M:%S')
    return tiempo_actual

def generar_token():
    p = os.urandom(4)
    token_bytes = base64.b64encode(p)
    return token_bytes.decode('utf-8')[:6]

def enviar_mensaje_telegram(chat_id, mensaje):
    URL_API_CHAT = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    params = {'chat_id': chat_id, 'text': mensaje}
    response = requests.get(URL_API_CHAT, params=params)

    if response.status_code != 200:
        messages.error(request, 'Error al enviar el mensaje:')

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