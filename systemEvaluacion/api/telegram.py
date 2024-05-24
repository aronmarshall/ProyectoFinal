from datetime import datetime
import threading
import telebot
import secrets
import string
import os

from bd import models


TOKEN = os.environ.get('TOKEN_TELEGRAM')
bot = telebot.TeleBot(TOKEN)

def consulta_token():
    token = models.TelegramData.objects.filter(estatus=True, enviar=True).values_list('tokens', flat=True).first()
    return token

@bot.message_handler(commands=['start', 'help'])
def mensaje_bienvenida(message:str)->None:
    """
    Maneja los comandos /start y /help y envía un mensaje de bienvenida al usuario.

    Args:
        message: El mensaje recibido que contiene el comando.
    """
    bot.reply_to(message, "Hola! Usa /solicitar_token para obtener un token o /mi_chat_id ")

@bot.message_handler(commands=['solicitar_token'])
def solicitar_token_handler(message:str)->None:
    """
    Maneja el comando /solicitar_token y envía un token OTP al usuario.

    Args:
        message: El mensaje recibido que contiene el comando.
    """
    usuario_o_telefono = message.chat.id  
    token = consulta_token()
    mensaje = f"Su token es: {token}"
    if consultar_token_enviados(usuario_o_telefono):
        mensaje=f"Haz generado tu token, valido por 3 minutos"
        enviar_token_usuario(usuario_o_telefono, mensaje)
    elif token_generador(message):
        mensaje = f"Su token es: {token}"
        actualizar_data(token, usuario_o_telefono)
        enviar_token_usuario(usuario_o_telefono, mensaje)
    else:
        mensaje = f"Caduco su token, reinicie el proceso, desde la web, oficial"
        enviar_token_usuario(usuario_o_telefono, mensaje)
        eliminar_data(usuario_o_telefono)

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
    
def actualizar_data(token, usuario_o_telefono):
    consultar = models.TelegramData.objects.filter(tokens=token).first()
    if consultar :
        id_token = models.TelegramData.objects.filter(tokens=token).values_list('id_token', flat=True).first()
        usuario = models.TelegramData.objects.filter(tokens=token).values_list('usuario', flat=True).first()
        tiempo = models.TelegramData.objects.filter(tokens=token).values_list('tiempo', flat=True).first()
        estatus = models.TelegramData.objects.filter(tokens=token).values_list('estatus', flat=True).first()
        enviar = models.TelegramData.objects.filter(tokens=token).values_list('enviar', flat=True).first()
        
        models.TelegramData.objects.filter(id_token=id_token).update(
            usuario=usuario,
            tokens=token,
            tiempo=tiempo,
            estatus=estatus,
            chat_id=usuario_o_telefono,
            enviar=False
        )

def consultar_token_enviados(usuario_o_telefono):
    consultar = models.TelegramData.objects.filter(chat_id=usuario_o_telefono, estatus=True, enviar=False).exists()
    if consultar:
        return True
    else:
        return False
    
def token_generador(message):
    usuario_o_telefono = message.chat.id  
    consultar_token=models.TelegramData.objects.filter(chat_id=usuario_o_telefono).exists()
    consultar_enviar=models.TelegramData.objects.filter(enviar=True).exists()
    if not consultar_token and consultar_enviar:
        return True
    else:
        return False
def eliminar_data(usuario_o_telefono):
    models.TelegramData.objects.filter(chat_id=usuario_o_telefono).delete()
    return True

def run_bot():
    bot.polling()
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()


#######NOTA HACER FUNCIÓN QUE SEA CAPAZ DE OBTENER USUARIO PASADO COMO VARIABLE


