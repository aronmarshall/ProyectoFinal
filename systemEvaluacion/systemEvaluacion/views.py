from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from datetime import datetime
from datetime import timezone
from bd import models
from systemEvaluacion import settings

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def inicio(request):
    return HttpResponse('Página de inicio')


def actualizar_info_cliente(cliente, intentos=1):
    fecha = datetime.now(timezone.utc)
    cliente.fecha_ultimo_intento = fecha
    cliente.intentos = intentos
    cliente.save() # update en bd
        

def registrar_cliente(ip: str) -> None:
    """
    Registra la información de un cliente que
    nunca se ha visto.

    
    returns: None 
    """
    fecha = datetime.now(timezone.utc)
    registro = models.Intentos(ip=ip, intentos=1,
                    fecha_ultimo_intento=fecha)
    registro.save()
    

def esta_en_ventana(tiempo_ultimo_intento: datetime, ventana: int) -> bool:
    """
    Determina si una fecha dada está dento de la ventana
    de tiempo dada de acuerdo a la fecha actual

    tiempo_ultimo_intento: datetime, fecha-hora a evaluar
    ventana: int, expresada en segundos
    return: bool, True si está dentro de la ventana 
    """
    actual = datetime.now(timezone.utc)
    diferencia = (actual - tiempo_ultimo_intento).seconds
    if diferencia <= ventana:
        return True
    return False
    
def puede_loguearse(request) -> bool:
    """
    Establece si dada una petición el cliente
    tiene oportunidades para loguearse

    request: petición de Django
    return -> bool: True si tiene posibilidades
    """
    ip = get_client_ip(request)
    try:
        cliente = models.Intentos.objects.get(ip=ip)
        if not esta_en_ventana(cliente.fecha_ultimo_intento,
                    settings.LIMITE_SEGUNDOS_LOGIN):
            actualizar_info_cliente(cliente)
            return True
        # Está en la ventana y ya lo conocemos
        if cliente.intentos >= settings.LIMITE_INTENTOS_LOGIN:
            actualizar_info_cliente(cliente, cliente.intentos)
            return False
        else: # estoy en ventana y tengo intentos
            actualizar_info_cliente(cliente, cliente.intentos + 1)
            return True
        
    except: # nunca se ha visto al cliente
        registrar_cliente(ip)
        return True
    

def loguear_usuario(request):
    if request.method == 'GET':
        ip = get_client_ip(request)        
        return render(request, 'login.html', {'ip': ip})
    elif request.method == 'POST':
        if not puede_loguearse(request):
            error = 'Agotaste tu límite de intentos, debes esperar %s segundos' % settings.LIMITE_SEGUNDOS_LOGIN
            return render(request, 'login.html', {'errores': error})
        usuario = request.POST.get('usuario', '')
        contra = request.POST.get('contra', '')
        if usuario == 'pepe' and contra == '1234':
            return redirect('/inicio')
        else: # malas credenciales
            error = 'Credenciales inválidas'
            return render(request, 'login.html', {'errores': error})
    else:
        error = "Método no soportado"
        return render(request, 'login.html')
        
