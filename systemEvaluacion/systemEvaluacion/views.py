from pyexpat.errors import messages
import secrets
import string
from urllib import request
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from datetime import datetime

from bd import models
from systemEvaluacion import settings
from api import telegram


import os
import base64
import crypt
import requests
import re
import threading

###########################################################Iniciamos el bot
bot_thread = threading.Thread(target=telegram.run_bot)
bot_thread.daemon = True
bot_thread.start()

##########################################################Manejo de sesión
def logout(request)->HttpResponse:
    """Cierra la sesión del usuario actual.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP que contiene los datos de la sesión del usuario.

    Returns:
        HttpResponse: Redirige al usuario a la vista de inicio de sesión.
    """
    request.session['logueado'] = False
    request.session.flush() 
    return redirect('login')        

###########################################################Inicio
def inicio(request)->HttpResponse:
    """
    Renderizado la página de inicio.
    Esta vista maneja las solicitudes a la página de inicio de la aplicación.
    Utiliza la función render de Django para devolver la plantilla 'inicio.html'.

    Args:
        request (HttpRequest): Objeto HttpRequest que contiene los datos de la solicitud.

    Returns:
        HttpResponse: La respuesta HTTP con el contenido renderizado de la plantilla 'inicio.html'.
    """
    return render(request, 'inicio.html')

#########################################################Registro
def registro_de_usuario(request)->HttpResponse:
    """
    Maneja el proceso de registro de un nuevo usuario.
    - Si el método de la solicitud es GET, renderizado la página de registro.
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
    """
        Genera contraseñas seguras, consultando la función generador_de_salt() y la contraseña pasada por
        el usuario.
    Args:
        contrasenia (str): Contraseña ingresada por el usuario

    Returns:
        str: Devuelve la variable hasheada 
    """
    salt_generado=generador_de_salt()
    hasheado = crypt.crypt(contrasenia, '$6$' + salt_generado)
    return hasheado

def insertar_datos_alumno_usuario(nombre_completo:str, matricula:str, usuario:str, contrasenia:str)->bool:
    """
        Inserta en la base de datos los datos pasados por el usuario para registrado.
    Args:
        nombre_completo (str): El nombre del usuario a registrar.
        matricula (str): matricula válida pasa por el usuario.
        usuario (str): El usuario pasado por el usuario que realiza el registro.
        contrasenia (str): contrasenia generada de forma segura.

    Returns:
        bool: devuelve True si el insert fue éxito.
    """
    nuevo_alumno = models.Alumno(nombre_completo=nombre_completo, matricula=matricula)
    nuevo_alumno.save()
    id_alumno = nuevo_alumno.id

    hasheado=contrasenia_segura(contrasenia)
    nuevo_usuario = models.Usuario(usuario=usuario, contrasenia=hasheado.encode(), alumno_id=id_alumno)
    nuevo_usuario.save()
    return True

#########################################################Login
def loguear_usuario(request)->HttpResponseRedirect:
    """
    Función que permite loguear a un usuario en el sistema.

    Args:
        request (HttpRequestRedirect): El objeto de solicitud HTTP que contiene los datos de la solicitud del usuario.

    Returns:
        HttpResponseRedirect: Redirige a la página de validación de token si el inicio de sesión es exitoso.
        Renderizado la página de inicio de sesión con un mensaje de error si falla el inicio de sesión.
    """

    if request.method == 'GET':
        return render(request, 'login.html')
    
    elif request.method == 'POST':

        usuario = request.POST.get('login_usuario')
        contrasenia = request.POST.get('login_contrasenia')
        
        request.session['usuario_iniciado'] = usuario
        token = generar_token()
        request.session['token'] = token
        
        if not verificar_existencia_usuario(usuario):
            messages.error(request, "Usuario o contraseña incorrectos")
            return render(request, 'login.html')
        else:
            if not consultar_hash(usuario, contrasenia):
                messages.error(request, "Usuario o contraseña incorrectos")
                return render(request, 'login.html')               
            else:
                return HttpResponseRedirect('usuarioTelegram')
    else:
        return render(request, 'login.html')

def consultar_hash(usuario:str, contrasenia:str)->bool:
    """
        Consulta si el usuario y contraseña pasados son válidos en la base datos.
    Args:
        usuario (str): Nombre de usuario pasado por usuario.
        contrasenia (str): Contraseña pasada por el usuario

    Returns:
        bool: Devuelve True, la contraseña hasheada es correcta, False en caso contrario.
    """
    usuario = models.Usuario.objects.filter(usuario=usuario).first()
    hasheado = usuario.contrasenia.decode('utf-8')
    partes = hasheado.split('$')
    complemento = '$' + partes[1] + '$' + partes[2]
    if hasheado == crypt.crypt(contrasenia, complemento):
        return True
    else:
        return False
    
###########################################################Telegram y token
def ingresar_usuario_telegram(request)->HttpResponseRedirect:

    if request.method == 'GET':
        return render(request, 'usuarioTelegram.html')
    elif request.method == 'POST':

        usuario_telegram = request.POST.get('usuario_telegram')
        usuario = request.session.get('usuario_iniciado')
        token = request.session.get('token')
        insertar_token_generador(usuario, token, usuario_telegram)
        return HttpResponseRedirect('validarToken')


def generar_token()->str:
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
def validar_token_telegram(request)->HttpResponseRedirect:
    """
        Valida el token de autenticación enviado a través de Telegram.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP que contiene los datos de la solicitud del usuario.

    Returns:
        HttpResponseRedirect: Redirige a la página de inicio si la validación es exitosa, o a la página login de sesión si falla.
    """
    if request.method == 'GET':
        return render(request, 'validarToken.html')
    elif request.method == 'POST':

        token_ingresado = request.POST.get('caracteres')
        usuario_sesion = request.session.get('usuario_iniciado')
        token = request.session.get('token')

        if not existe_token_en_sesion(usuario_sesion, token_ingresado):
            messages.error(request, f'El token {token} no es correcto.')
            eliminar_token(usuario_sesion, token)
            request.session.flush()
            purgar_tokens(usuario_sesion)
            return HttpResponseRedirect('login')
        else:
            if not tiempo_valido(token):
                messages.error(request, f'El token {token} ya expiro.')
                eliminar_token(usuario_sesion, token)
                request.session.flush()
                purgar_tokens(usuario_sesion)
                return HttpResponseRedirect('login')
            else:
                if token_ingresado == token:
                    eliminar_token(usuario_sesion, token)
                    purgar_tokens(usuario_sesion)
                    return HttpResponseRedirect('inicio')
                else:
                    messages.error(request, f'El token {token} no es correcto.')
                    eliminar_token(usuario_sesion, token)
                    request.session.flush()
                    purgar_tokens(usuario_sesion)
                    return HttpResponseRedirect('login') 

def insertar_token_generador(usuario:str, token:str, usuario_telegram:str)->str:
    """
        Inserta el token generado en la base de datos para el usuario especificado.

    Args:
        usuario (str): El nombre del usuario para el cual se genera el token.
        token (str): El token generado que será almacenado en la base de datos.
        usuario_telegram: El usuario de telegram. 
    Returns:
        str: El token generado.
    """
    usuario = usuario
    tokens = token
    tiempo = obtener_tiempo_horas_minutos()
    enviar = True
    usuario_telegram = usuario_telegram
    
    guardar_estado = models.TelegramData(usuario=usuario, tokens=tokens, tiempo=tiempo, enviar=enviar, usuarioTelegram=usuario_telegram)
    guardar_estado.save()
    return token

def existe_token_en_sesion(usuario_sesion:str, token_ingresado:str)->bool:
    """
        Verifica si el token ingresado existe en la sesión del usuario.

    Args:
        usuario_sesion (str): El nombre del usuario que tiene la sesión activa.
        token_ingresado (str): El token ingresado por el usuario para validación.

    Returns:
        bool: True si el token ingresado existe en la sesión del usuario, False en caso contrario.
    """
    consultar=models.TelegramData.objects.filter(usuario=usuario_sesion, tokens=token_ingresado).exists()
    if consultar:
        return True
    else:
        return False

def eliminar_token(usuario_sesion:str, token:str)->bool:
    """
        Elimina un token de la base de datos asociado al usuario especificado.

    Args:
        usuario_sesion (str): El nombre del usuario que tiene la sesión activa.
        token (str): El token que se desea eliminar de la base de datos.

    Returns:
        bool: True si se elimina correctamente el token.
    """
    token_ingresado=token
    if existe_token_en_sesion(usuario_sesion, token_ingresado):
        vaciar_token=models.TelegramData.objects.filter(tokens=token)
        vaciar_token.delete()
        return True
    
def purgar_tokens(usuario_sesion:str)->bool:
    vaciar_token=models.TelegramData.objects.filter(usuario=usuario_sesion)
    vaciar_token.delete()
    return True

def tiempo_valido(token:str)->bool:
    """
        Verifica si un token aún está dentro de su tiempo de validez.

    Args:
        token (str): El token cuyo tiempo de validez se desea verificar.

    Returns:
        bool: True si el token está dentro de su tiempo de validez, False si ha expirado.
    """
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

def consultar_tiempo_almacenado(token:str)->datetime:
    """
        Consulta el tiempo almacenado asociado a un token en la base de datos.

    Args:
        token (str): El token del cual se desea obtener el tiempo almacenado.

    Returns:
        datetime: El tiempo almacenado asociado al token.
    """
    consulta_tiempo = models.TelegramData.objects.filter(tokens=token).values_list('tiempo', flat=True).first()
    return consulta_tiempo
