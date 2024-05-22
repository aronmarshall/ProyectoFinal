from datetime import datetime
import threading
import telebot
import secrets
import string
import os

from bd import models

TOKEN = os.environ.get('TOKEN_TELEGRAM')
bot = telebot.TeleBot(TOKEN)

def generar_token() -> str:
    """
    Genera un token aleatorio de 6 caracteres compuesto por letras mayúsculas y dígitos.

    Returns:
        str: El token generado.
    """
    alphabet = string.ascii_uppercase + string.digits
    token = "".join(secrets.choice(alphabet) for _ in range(6))
    return token

@bot.message_handler(commands=['start', 'help'])
def mensaje_bienvenida(message:str)->None:
    """
    Maneja los comandos /start y /help y envía un mensaje de bienvenida al usuario.

    Args:
        message: El mensaje recibido que contiene el comando.
    """
    bot.reply_to(message, "Hola! Usa /solicitar_token para obtener un token.")

@bot.message_handler(commands=['solicitar_token'])
def solicitar_token_handler(message:str)->None:
    """
    Maneja el comando /solicitar_token y envía un token OTP al usuario.

    Args:
        message: El mensaje recibido que contiene el comando.
    """
    usuario_o_telefono = message.chat.id  
    token = generar_token()
    mensaje = f"Su token es: {token}"
    insertar_token_db(message)
    enviar_token_usuario(usuario_o_telefono, mensaje)

def enviar_token_usuario(usuario_o_telefono, mensaje) -> None:
    """
    Envía el token OTP al usuario a través de la API de Telegram.

    Args:
        usuario_o_telefono: El nombre de usuario o ID del chat de Telegram.
        mensaje: El mensaje que contiene el token OTP.
    """
    try:
        bot.send_message(usuario_o_telefono, mensaje)
    except Exception as e:
        raise Exception(f'Error al enviar el mensaje a Telegram: {e}')

@bot.message_handler(commands=['mi_chat_id'])
def enviar_chat_id(message:str)-> str:

    chat_id = message.chat.id
    bot.reply_to(message, f"Tu chat ID es: {chat_id}")


def run_bot():
    bot.polling()
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

def obtener_tiempo_horas_minutos()->str:
    """
    Obtiene la hora actual en formato HH:MM.

    Returns:
        str: La hora actual en formato HH:MM.
    """
    tiempo = datetime.now()
    tiempo_actual = tiempo.strftime('%H:%M')
    return tiempo_actual

#######NOTA HACER FUNCIÓN QUE SEA CAPAZ DE OBTENER USUARIO PASADO COMO VARIABLE
def insertar_token_db(message:str)->bool:
    usuario_telegram = message.from_user.username
    nombre_usuario = "emilio"
    token = generar_token()
    tiempo = obtener_tiempo_horas_minutos()
    estatus = 'True'

    guarda_info_token = models.TelegramToken(usuario_telegram=usuario_telegram, nombre_usuario=nombre_usuario,
                                                tokens=token, tiempo=tiempo, estatus=estatus)
    guarda_info_token.save()
    return True


