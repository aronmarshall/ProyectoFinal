from bd import models
from systemEvaluacion.views import obtener_tiempo_horas_minutos


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