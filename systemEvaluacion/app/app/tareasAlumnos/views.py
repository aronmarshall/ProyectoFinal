from pyexpat.errors import messages  
from django.contrib import messages  
from django.http import HttpResponse, HttpResponseRedirect  
from django.shortcuts import render, redirect  
from datetime import datetime, date  
from django.utils import timezone


from bd import models  
from systemEvaluacion import settings  
from api import telegram 
from api import recaptcha  


import os
import base64
import crypt
import re
import threading
import secrets
import string
import random


#######################################################################
def listar_tareas_disponibles(request)->HttpResponse:
    """
    Lista las tareas disponibles en función de la sesión del usuario y el método de solicitud.
    
    Args:
        request: Objeto HttpRequest que contiene metadatos sobre la solicitud.
        
    Returns:
        Objeto HttpResponse con la plantilla de tareas renderizada o una respuesta de redirección.
    """
    if request.session.get('maestro'):  # Verifica si el usuario es un maestro
        return redirect('/inicio_maestro')  
    else:
        if request.method == 'GET':  
            
            hoy = fecha_actual()  
            tareas_validas = obtener_tareas_con_estado(hoy)  

            messages.info(request, f'Fecha: {hoy}')  # Añade un mensaje flash con la fecha actual
            return render(request, 'tareas_disponibles.html', {'tareas_validas': tareas_validas})  # Renderiza la plantilla de tareas con las tareas válidas
        elif request.method == 'POST':  
            return render(request, 'tareas_disponibles.html')  

def fecha_valida(fecha_inicio:date)->bool:
    """
    Verifica si la fecha de inicio dada es válida (hoy o posterior).
    
    Args:
        fecha_inicio: Objeto date que representa la fecha de inicio.
        
    Returns:
        bool: True si la fecha de inicio es válida, False en caso contrario.
    """
    hoy = date.today()  
    return fecha_inicio >= hoy and fecha_inicio <= hoy  # Verifica si la fecha de inicio es hoy o posterior

def fecha_actual() -> date:
    """
    Obtiene la fecha actual.
    
    Returns:
        date: Fecha actual.
    """
    return date.today()  

def obtener_tareas_con_estado(hoy:date)->list:
    """
    Obtiene las tareas con su estado en función de la fecha actual.
    
    Args:
        hoy: Objeto date que representa la fecha actual.
        
    Returns:
        list: Lista de tareas con su estado.
    """
    tareas_validas = validar_tareas_por_fecha(hoy)  
    tareas_con_estado = []  # Inicializa una lista vacía para contener las tareas con su estado

    for tarea in models.Crear_tarea.objects.all():  
        tarea.estado_valido = fecha_valida(tarea.fecha_inicio)  
        tareas_con_estado.append(tarea)  # Añade la tarea con su estado a la lista
    return tareas_con_estado  # Devuelve la lista de tareas con su estado

def validar_tareas_por_fecha(hoy:date)->str:
    """
    Valida las tareas en función de sus fechas de inicio y cierre.
    
    Args:
        hoy: Objeto date que representa la fecha actual.
        
    Returns:
        QuerySet: Conjunto de consultas de tareas que son válidas en función de la fecha actual.
    """
    return models.Crear_tarea.objects.filter(fecha_inicio__lte=hoy, fecha_cierre__gte=hoy)  # Filtra las tareas que son válidas en función de sus fechas de inicio y cierre
########################################################################
def subir_tarea(request):
    if request.session.get('maestro'):  
        return redirect('/inicio_maestro')  
    else:
        if request.method == 'GET':  
            return render(request, 'subir_tareas.html')      
        elif request.method == 'POST':  
            nombre_tarea = request.POST.get('nombre_tarea')
            detalles_tarea = consultar_detalles_tarea(nombre_tarea)

            #Obtenemos data en session
            request.session['nombre_entrega_tarea'] = nombre_tarea 

            return render(request, 'subir_tareas.html', {'detalles_tarea': detalles_tarea})

def consultar_detalles_tarea(nombre_tarea): 
    try:
        tarea = models.Crear_tarea.objects.get(nombre=nombre_tarea)
        detalles_tarea = {
            'nombre': tarea.nombre,
            'descripcion': tarea.descripcion_general,
            'fecha_inicio': tarea.fecha_inicio,
            'fecha_cierre': tarea.fecha_cierre,
        }
        return detalles_tarea
    except models.Crear_tarea.DoesNotExist:
        return None

def entregar_tarea(request):
    if request.session.get('maestro'):  
        return redirect('/inicio_maestro')  
    else:
        if request.method == 'GET':  
               return render(request, 'inicio.html')      
        elif request.method == 'POST':
            try:
                id_entrega = id_num()
                alumno = "Emilio" #hardcodeado
                tarea = request.session.get('nombre_entrega_tarea')
                hora_entrega = obtener_hora_actual()
                puntaje = 6 #hardcodeado
                entrega_tarea = request.FILES.get('archivo_tarea')

                almacenar_tarea = models.Entrega(
                    id_entrega=id_entrega, 
                    alumno=alumno, 
                    tarea=tarea,
                    hora_entrega=hora_entrega, 
                    puntaje=puntaje, 
                    codigo_entrega=entrega_tarea
                    )
                
                almacenar_tarea.save()
                
                messages.info(request, f'Se entrego la tarea.')
                return redirect('/inicio')

            except Exception as e:
                messages.error(request, f'Error al entregar la tarea: {str(e)}')
                return redirect('/inicio')

def id_num()->int:
    """
    Genera un número de referencia de 4 dígitos.
    
    Returns:
        int: Número de referencia de 4 dígitos.
    """
    return ''.join(str(random.randint(0, 9)) for _ in range(4))

def obtener_hora_actual():
    return timezone.now()