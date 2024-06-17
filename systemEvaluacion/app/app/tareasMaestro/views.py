from pyexpat.errors import messages
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from datetime import datetime, timezone

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

def crear_tarea(request)->HttpResponse:
    """
    Crea una nueva tarea basada en los datos proporcionados por el formulario POST.
    
    Args:
        request: Objeto HttpRequest que contiene metadatos sobre la solicitud.
        
    Returns:
        HttpResponse: Renderiza la página de inicio del maestro después de crear la tarea.
    """
    if not request.session.get('maestro'):
        return redirect('/inicio') 
    else:
        if request.method == 'GET':
            return render(request, 'crear_tarea.html')  
        elif request.method == 'POST':
            # Obtiene datos del formulario y genera un id de tarea
            cadena_numeros = nrc()
            id_tarea = cadena_numeros
            nombre_eje = request.POST.get('nombre_eje')
            descripcion = request.POST.get('descripcion')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_cierre = request.POST.get('fecha_cierre')
            entrada = request.POST.get('entrada')
            salida = request.POST.get('salida')
            salida_ejemplo = request.FILES.get('salida_ejemplo')

            # Inserta los datos de la nueva tarea en la base de datos
            insertar_datos = models.Crear_tarea(
                id_tarea=id_tarea, 
                nombre=nombre_eje, 
                descripcion_general=descripcion, 
                fecha_inicio=fecha_inicio, 
                fecha_cierre=fecha_cierre, 
                entrada_esperada=entrada, 
                salida_esperada=salida, 
                archivo_evaluar=salida_ejemplo
            )
            insertar_datos.save()

            messages.info(request, f'Se insertó la actividad {nombre_eje}')
            return render(request, 'inicio_maestro.html')

def nrc()->int:
    """
    Genera un número de referencia de 4 dígitos.
    
    Returns:
        int: Número de referencia de 4 dígitos.
    """
    return ''.join(str(random.randint(0, 9)) for _ in range(4))

def listar_mis_tareas(request)->HttpResponse:
    """
    Lista todas las tareas creadas por el maestro.
    
    Args:
        request: Objeto HttpRequest que contiene metadatos sobre la solicitud.
        
    Returns:
        HttpResponse: Renderiza la página con la lista de tareas del maestro.
    """
    if not request.session.get('maestro'):
        return redirect('/inicio')  
    else:
        if request.method == 'POST':
            return render(request, 'listar_mis_tareas.html')
        elif request.method == 'GET':
            consultar_mis_tareas = models.Crear_tarea.objects.all()  # Obtiene todas las tareas del maestro
            messages.info(request, f'Se encontraron {consultar_mis_tareas.count()} tareas.')
            return render(request, 'listar_mis_tareas.html', {'tareas': consultar_mis_tareas})

def eliminar_tareas(request)->HttpResponse:
    """
    Elimina una tarea específica basada en el ID proporcionado por el formulario POST.
    
    Args:
        request: Objeto HttpRequest que contiene metadatos sobre la solicitud.
        
    Returns:
        HttpResponse: Redirige a la página con la lista de tareas después de intentar eliminar una tarea.
    """
    if not request.session.get('maestro'):
        return redirect('/inicio')  
    else:
        if request.method == 'GET':
            return render(request, 'listar_mis_tareas.html')
        elif request.method == 'POST':
            eliminar = request.POST.get('elimina_tarea')
            try:
                eliminar_numero = int(eliminar)  # Convierte el ID a un número entero
            
            except ValueError:
            
                messages.error(request, 'Por favor, ingresa solo números enteros.')
                return redirect('/listar_mis_tareas')

            if not existe_ejercicio(eliminar_numero):
                messages.success(request, f'La tarea "{eliminar_numero}" no existe.')
                return redirect('/listar_mis_tareas')
            else:
                try:
                    tarea = models.Crear_tarea.objects.get(id_tarea=eliminar_numero)
                    tarea.delete()  # Elimina la tarea de la base de datos
                    messages.success(request, f'Tarea "{tarea.nombre}" eliminada correctamente.')
                    return redirect('/listar_mis_tareas')
                except models.Crear_tarea.DoesNotExist:
                    messages.error(request, f'La tarea "{eliminar_numero}" no existe.')
                    return redirect('/listar_mis_tareas')

def existe_ejercicio(eliminar:int)->bool:
    """
    Verifica si una tarea con el ID especificado existe.
    
    Args:
        eliminar: ID de la tarea a verificar.
        
    Returns:
        bool: True si la tarea existe, False en caso contrario.
    """
    existe = models.Crear_tarea.objects.filter(id_tarea=eliminar).exists()
    return existe

def respuestas_estudiantes(request)->HttpResponse:
    """
    Renderiza la página para mostrar las respuestas de los estudiantes.
    
    Args:
        request: Objeto HttpRequest que contiene metadatos sobre la solicitud.
        
    Returns:
        HttpResponse: Renderiza la página de respuestas de los estudiantes.
    """
    if not request.session.get('maestro'):
        return redirect('/inicio')  
    else:
        return render(request, 'listar_mis_tareas.html')
