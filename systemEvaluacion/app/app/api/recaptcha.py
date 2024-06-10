from systemEvaluacion import settings
import requests
 
def verifica_captchat_web(captcha):
    datosVerificacion = {
        'secret': settings.RECAPTCHA_PRIVATE_KEY,  
        'response': captcha
    }
    respuesta = requests.post('https://www.google.com/recaptcha/api/siteverify', data=datosVerificacion)
    resultadoCaptcha = respuesta.json()
    return resultadoCaptcha