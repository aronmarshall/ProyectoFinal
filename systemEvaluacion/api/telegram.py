from datetime import datetime
import threading
import telebot
import os

from bd import models
from systemEvaluacion import views


TOKEN = os.environ.get('TOKEN_TELEGRAM')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def mensaje_bienvenida(message:str):
    """
    Maneja los comandos /start y /help y envía un mensaje de bienvenida al usuario.

    Args:
        message: El mensaje recibido que contiene el comando.
    """
    bot.reply_to(message, "Hola! Usa /solicitar_token para obtener un token o /my_user ")

@bot.message_handler(commands=['solicitar_token'])
def solicitar_token_handler(message:str):
    """
    Maneja el comando /solicitar_token y envía un token OTP al usuario.

    Args:
        message: El mensaje recibido que contiene el comando.
    """
    usuario_o_telefono = message.chat.id  
    username = message.from_user.username

    token = existe_token_de_usuario(username)
    mensaje = f"# {token}"
    enviar_token_usuario(usuario_o_telefono, mensaje)

def existe_token_de_usuario(username):
    token_valido = models.TelegramData.objects.filter(usuarioTelegram=username, enviar=True).values_list('tokens', flat=True).first()
    if not token_valido:
            token_enviado = models.TelegramData.objects.filter(usuarioTelegram=username, enviar=False).order_by('-tiempo').values_list('tokens', flat=True).first()
            if token_enviado:
                return token_enviado
            else:
                mensaje = f'Lo siento, tu usuario {username}, no ha iniciado el proceso de registro.'
                return mensaje
    else:
        models.TelegramData.objects.filter(tokens=token_valido, enviar=True).update(enviar=False)
        return token_valido

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

@bot.message_handler(commands=['my_user'])
def enviar_usuario(message:str)-> str:
    username = message.from_user.username
    bot.reply_to(message, f"Tu usuario es: {username}")
    


def run_bot():
    bot.polling()
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()



