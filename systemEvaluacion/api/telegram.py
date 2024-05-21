import requests
import os
import base64
from datetime import datetime
from bd import models

TOKEN = '7199611399:AAHrE8s0MW6oLz-MmhI6RzFDs-TCFaxq7q8'
URL = f'https://api.telegram.org/bot{TOKEN}/getUpdates'


def obtener_chat_id(usuario_telegram):
    """Obtiene el chat ID de un usuario de Telegram dado su nombre de usuario.
    Args:
        usuario_telegram (str): El nombre de usuario de Telegram.

    Raises:
        Exception: Si ocurre un error al realizar la solicitud a la API de Telegram.

    Returns:
        int: El chat ID del usuario de Telegram si se encuentra, de lo contrario None.
    """
    try:
        response = requests.get(URL)
        response.raise_for_status()
        data = response.json()
        for update in data['result']:
            if 'message' in update and 'chat' in update['message'] and 'username' in update['message']['chat']:
                if update['message']['chat']['username'] == usuario_telegram:
                    return update['message']['chat']['id']
        return None
    except requests.exceptions.RequestException as e:
        raise Exception(f'Error al obtener el chat ID: {e}')


def obtener_tiempo():
    """
    Obtiene la hora actual en formato HH:MM:SS.

    Returns:
        str: La hora actual en formato HH:MM:SS.
    """
    tiempo = datetime.now()
    tiempo_actual = tiempo.strftime('%H:%M:%S')
    return tiempo_actual


def generar_token():
    """
    Genera un token aleatorio de 6 caracteres.

    Returns:
        str: Un token aleatorio de 6 caracteres.
    """
    p = os.urandom(4)
    token_bytes = base64.b64encode(p)
    return token_bytes.decode('utf-8')[:6]


def enviar_mensaje_telegram(chat_id, mensaje):
    """
    Envía un mensaje a un usuario de Telegram.

    Args:
        chat_id (int): El ID del chat de Telegram al que se enviará el mensaje.
        mensaje (str): El contenido del mensaje a enviar.

    Raises:
        Exception: Si ocurre un error al realizar la solicitud a la API de Telegram.
    """
    URL_API_CHAT = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    params = {'chat_id': chat_id, 'text': mensaje}
    try:
        response = requests.get(URL_API_CHAT, params=params)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise Exception(f'Error al enviar el mensaje a Telegram: {e}')


def procesar_doble_factor(usuario_telegram):
    """
    Coordina el proceso de autenticación de doble factor para un usuario de Telegram.

    Args:
        usuario_telegram (str): El nombre de usuario de Telegram.

    Raises:
        ValueError: Si el usuario no ha enviado mensajes al bot de Telegram.
        Exception: Si ocurre un error inesperado durante el proceso.

    Returns:
        bool: True si el proceso de autenticación de doble factor fue exitoso, False en caso contrario.
    """
    try:
        chat_id = obtener_chat_id(usuario_telegram)
        if chat_id:
            token = generar_token()
            tiempo = obtener_tiempo()
            guardar_token = models.validaToken(tokens=token, tiempo=tiempo)
            guardar_token.save()
            enviar_mensaje_telegram(chat_id, f'Hola {usuario_telegram}, tu Token es: {token}')
            return True
        else:
            ValueError(f'El usuario {usuario_telegram} no ha enviado mensajes al bot.')
            return False
    except ValueError as ve:
        raise ve  # Maneja el error de usuario no encontrado
    except Exception as e:
        raise Exception(f'Error inesperado: {e}')
