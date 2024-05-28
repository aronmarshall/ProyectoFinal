from pyexpat.errors import messages
import secrets
import string
from urllib import request
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from datetime import datetime, timedelta

from bd import models
from systemEvaluacion import settings
from api import telegram


import os
import base64
import crypt
import requests
import re
import threading
import pytz

###########################################################Arranque del bot
bot_thread = threading.Thread(target=telegram.run_bot)
bot_thread.daemon = True
bot_thread.start()
##########################################################Manejo de sesión

def logout(request):
    request.session['logueado'] = False
    request.session.flush() # borra la sesión
    return redirect('login')        

###########################################################Inicio
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

#########################################################Registro
def registro_de_usuario(request):
    """
    Maneja el proceso de registro de un nuevo usuario.

    - Si el método de la solicitud es GET, renderiza la página de registro.
    - Si el método de la solicitud es POST, procesa los datos del formulario para registrar al usuario.

    Args:
        request (HttpRequest): Objeto HttpRequest que puede ser de tipo GET o POST.

    Returns:
        HttpResponse: Renderización de la página de registro o mensajes de error según el caso.
    """
    if request.method == 'GET':
        return render(request, 'registro.html')

    elif request.method == 'POST':

        nombre_completo = request.POST.get('nombre_completo')
        matricula = request.POST.get('matricula')
        usuario = request.POST.get('usuario_nuevo')
        contrasenia = request.POST.get('contrasenia')
        contrasenia_confirma = request.POST.get('contrasenia_confirma')

        if verificar_existencia_usuario(usuario):
            messages.info(request, f'Lo siento, el usuario {usuario} esta en uso.')
            return render(request, 'registro.html')
        else:
            if existe_matricula_bd(matricula):
                messages.info(request, f'Lo siento, la matrícula {matricula} esta registrada.')
                return render(request, 'registro.html')
            else:
                if not validar_politica_matricula(matricula):
                    messages.info(request, f'Lo siento, la matrícula {matricula} no cumple con las políticas.')
                    return render(request, 'registro.html')
                else:
                    if not politica_de_contrasenia(contrasenia):
                        messages.info(request, f'Lo siento, la contraseña debe contener mínimo 10 carácteres, mayúsculas, minúsuclas, dígitos, al menos un carácter especial.')
                        return render(request, 'registro.html')
                    else:
                        if not comparar_contrasenias(contrasenia, contrasenia_confirma):
                            messages.info(request, 'Las contraseñas no son iguales.')
                            return render(request, 'registro.html')
                        else:
                            if not insertar_datos_alumno_usuario(nombre_completo, matricula, 
                                                                usuario, contrasenia):
                                messages.error(request, 'No se concreto la creación.')
                                return render(request, 'registro.html')
                            else:
                                messages.info(request, f'Se creo con éxito el usuario {usuario}.')
                                return render(request, 'registro.html')

def verificar_existencia_usuario(usuario:str)->bool:
    """
    Verifica si un usuario ya está registrado en la base de datos.

    Args:
        usuario (str): Nombre de usuario a verificar.

    Returns:
        bool: True si el usuario ya existe en la base de datos, False en caso contrario.
    """
    existe_usuario_registrado = models.Usuario.objects.filter(usuario=usuario).exists()
    if existe_usuario_registrado:
        return True
    else:
        return False

def existe_matricula_bd(matricula:str)->bool:
    """
    Verifica si una matrícula ya está registrada en la base de datos.

    Args:
        matricula (str): Matrícula a verificar.

    Returns:
        bool: True si la matrícula ya existe en la base de datos, False en caso contrario.
    """
    matricula_registrada = models.Alumno.objects.filter(matricula=matricula).exists()
    if matricula_registrada:
        return True
    else:
        return False

def validar_politica_matricula(matricula:str)->bool:
    """
    Valida si la matrícula cumple con el formato requerido por las políticas.

    El formato requerido es:
    - Debe comenzar con dos letras 'z' o 's' (mayúsculas o minúsculas).
    - Seguido de 8 dígitos numéricos.

    Args:
        matricula (str): Matrícula a validar.

    Returns:
        bool: True si la matrícula cumple con el formato requerido, False en caso contrario.
    """
    politica_de_matricula = r'^[zZ|sS]{2}\d{8}$'
    if re.match(politica_de_matricula, matricula):
        return True
    else:
        return False
    
def politica_de_contrasenia(contrasenia:str)->bool:
    """
    Valida si una contraseña cumple con las políticas de seguridad establecidas.

    Las políticas de seguridad para la contraseña son:
    - Debe contener al menos 10 caracteres.
    - Debe contener al menos una letra mayúscula.
    - Debe contener al menos una letra minúscula.
    - Debe contener al menos un dígito.
    - Debe contener al menos un carácter especial (por ejemplo, @$!%*?&).

    Args:
        contrasenia (str): Contraseña a validar.

    Returns:
        bool: True si la contraseña cumple con todas las políticas de seguridad, False en caso contrario.
    """
    patron_contrasenia = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{10,}$'
    if re.match (patron_contrasenia, contrasenia):
        return True
    else:
        return False
    
def comparar_contrasenias(contrasenia:str, contrasenia_confirma:str)->bool:
    """
    Compara dos contraseñas para verificar si son iguales.

    Args:
        contrasenia (str): La primera contraseña.
        contrasenia_confirma (str): La segunda contraseña para confirmar.

    Returns:
        bool: True si las contraseñas son iguales, False en caso contrario.
    """
    if contrasenia == contrasenia_confirma:
        return True
    else:
        return False

def generador_de_salt()->str:
    """
    Genera un valor de salt único para la seguridad de la contraseña.

    El proceso de generación de salt es el siguiente:
    - Genera un valor aleatorio de 16 bytes.
    - Codifica el valor aleatorio en base64.
    - Verifica que el valor generado no exista ya en la base de datos (para garantizar unicidad).
    - Guarda el valor de salt en la base de datos para evitar colisiones futuras.
    - Retorna el valor de salt generado.

    Returns:
        str: El valor de salt generado y codificado en base64.
    """
    while True:
        valor_aleatorio = os.urandom(16)
        valor_generado_salt = base64.b64encode(valor_aleatorio).decode('utf-8')
        existe_salt_generado = models.TokenOcupados.objects.filter(token=valor_generado_salt).exists()
        if not existe_salt_generado:
            salt_guardado = models.TokenOcupados(token=valor_generado_salt)
            salt_guardado.save()
            break
    return valor_generado_salt

def contrasenia_segura(contrasenia:str)->str:
    salt_generado=generador_de_salt()
    hasheado = crypt.crypt(contrasenia, '$6$' + salt_generado)
    return hasheado


def insertar_datos_alumno_usuario(nombre_completo:str, matricula:str, usuario:str, contrasenia:str)->bool:

    nuevo_alumno = models.Alumno(nombre_completo=nombre_completo, matricula=matricula)
    nuevo_alumno.save()
    id_alumno = nuevo_alumno.id

    hasheado=contrasenia_segura(contrasenia)
    nuevo_usuario = models.Usuario(usuario=usuario, contrasenia=hasheado.encode(), alumno_id=id_alumno)
    nuevo_usuario.save()
    return True


#########################################################Login
def loguear_usuario(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    
    elif request.method == 'POST':

        usuario = request.POST.get('login_usuario')
        contrasenia = request.POST.get('login_contrasenia')
        
        request.session['usuario_iniciado'] = usuario
        token = generar_token()
        request.session['token'] = token
        insertar_token_generador(usuario, token)
        
        if not verificar_existencia_usuario(usuario):
            messages.error(request, "Usuario o contraseña incorrectos")
            return render(request, 'login.html')
        else:
            if not consultar_hash(usuario, contrasenia):
                messages.error(request, "Usuario o contraseña incorrectos")
                return render(request, 'login.html')               
            else:

                    return HttpResponseRedirect('validarToken')
    else:
        return render(request, 'login.html')

def consultar_hash(usuario:str, contrasenia:str)->bool: 

    usuario = models.Usuario.objects.filter(usuario=usuario).first()
    hasheado = usuario.contrasenia.decode('utf-8')
    partes = hasheado.split('$')
    complemento = '$' + partes[1] + '$' + partes[2]
    if hasheado == crypt.crypt(contrasenia, complemento):
        return True
    else:
        return False
    
#################################################################
def generar_token() -> str:
    """
    Genera un token aleatorio de 6 caracteres compuesto por letras mayúsculas y dígitos.

    Returns:
        str: El token generado.
    """
    alphabet = string.ascii_uppercase + string.digits
    token = "".join(secrets.choice(alphabet) for _ in range(6))
    return token

def obtener_tiempo_horas_minutos()->str:
    """
    Obtiene la hora actual en formato HH:MM:SS.

    Returns:
        str: La hora actual en formato HH:MM:SS.
    """
    tiempo = datetime.now()
    tiempo_actual = tiempo.strftime('%H:%M:%S')
    return tiempo_actual


#################################################################Doble factor autenticación
def validar_token_telegram(request):
    if request.method == 'GET':
        
        return render(request, 'validarToken.html')
    elif request.method == 'POST':

        token_ingresado = request.POST.get('caracteres')

        usuario_sesion = request.session.get('usuario_iniciado')
        token = request.session.get('token')

        if not existe_token_en_sesion(usuario_sesion, token_ingresado):
            #Eliminar el token
            #Destruir sesion
            eliminar_token(usuario_sesion, token)
            return HttpResponseRedirect('login')
        else:
            if not tiempo_valido(token):
                messages.error(request, f'El token {token} ya expiro.')
                eliminar_token(usuario_sesion, token)
                return HttpResponseRedirect('login')
            else:
                eliminar_token(usuario_sesion, token)
                return HttpResponseRedirect('inicio')
        
def insertar_token_generador(usuario, token):
    usuario = usuario
    tokens = token
    tiempo = obtener_tiempo_horas_minutos()
    estatus = True
    enviar = True
    
    guardar_estado = models.TelegramData(usuario=usuario, tokens=tokens, tiempo=tiempo, estatus=estatus, enviar=enviar)
    guardar_estado.save()
    return token

def existe_token_en_sesion(usuario_sesion, token_ingresado):
    consultar=models.TelegramData.objects.filter(usuario=usuario_sesion, tokens=token_ingresado).exists()
    if consultar:
        return True
    else:
        return False

def eliminar_token(usuario_sesion, token):
    token_ingresado=token
    if existe_token_en_sesion(usuario_sesion, token_ingresado):
        vaciar_token=models.TelegramData.objects.filter(tokens=token)
        vaciar_token.delete()
        return True
    
def tiempo_valido(token):
    tiempo_consultado=consultar_tiempo_almacenado(token)
    tiempo_actual = datetime.now().time()
    if tiempo_consultado:
        diferencia_tiempo = (
            tiempo_actual.hour * 3600 + tiempo_actual.minute * 60 + tiempo_actual.second
        ) - (
            tiempo_consultado.hour * 3600 + tiempo_consultado.minute * 60 + tiempo_consultado.second
        )
        if diferencia_tiempo > settings.TIEMPO_DE_VIDA_TOKEN * 60:
            return False
        else:
            return True

def consultar_tiempo_almacenado(token):
    consulta_tiempo = models.TelegramData.objects.filter(tokens=token).values_list('tiempo', flat=True).first()
    return consulta_tiempo
