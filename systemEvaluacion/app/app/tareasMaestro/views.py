from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from datetime import datetime, timezone

from bd import models
from systemEvaluacion import settings

import os
import random
import logging

logging.basicConfig(filename='logs/app.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

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
            cadena_numeros = nrc()
            id_tarea = cadena_numeros
            nombre_eje = request.POST.get('nombre_eje')
            profesor = request.session.get('profesor')
            descripcion = request.POST.get('descripcion')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_cierre = request.POST.get('fecha_cierre')
            entrada = request.POST.get('entrada')
            salida = request.POST.get('salida')
            
            if titulo_tarea_igual(nombre_eje):
                messages.info(request, f'Lo siento, la tarea {nombre_eje} tiene nombre duplicado.')
                logging.info(f'Se ha intentado crear una tarea con un nombre identico {nombre_eje}')
                return render(request, 'inicio_maestro.html')
            else:
                insertar_datos = models.Crear_tarea(
                    id_tarea=id_tarea, 
                    nombre=nombre_eje,
                    profesor=profesor, 
                    descripcion_general=descripcion, 
                    fecha_inicio=fecha_inicio, 
                    fecha_cierre=fecha_cierre, 
                    entrada_esperada=entrada, 
                    salida_esperada=salida
                )
                insertar_datos.save()
                logging.info(f'Se ha creado con exito la siguente tarea {nombre_eje}')

                messages.info(request, f'Se insertó la actividad "{nombre_eje}".')
                return render(request, 'inicio_maestro.html')

def titulo_tarea_igual(nombre_eje:str)->bool:
    existe_nombre_tarea = models.Crear_tarea.objects.filter(nombre=nombre_eje).exists()
    if existe_nombre_tarea:
        return True
    else:
        return False

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
            profesor = request.session.get('profesor')
            consultar_mis_tareas = models.Crear_tarea.objects.filter(profesor=profesor) 
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
                eliminar_numero = int(eliminar)  
            
            except ValueError:
            
                messages.error(request, 'Por favor, ingresa solo números enteros.')
                return redirect('/listar_mis_tareas')

            if not existe_ejercicio(eliminar_numero):
                messages.success(request, f'La tarea "{eliminar_numero}" no existe.')
                return redirect('/listar_mis_tareas')
            else:
                try:
                    tarea = models.Crear_tarea.objects.get(id_tarea=eliminar_numero)
                    tarea.delete()  
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
    """_summary_
    Muestra las respuestas de todos los estudiantes.
    """
    if not request.session.get('maestro'):
        return redirect('/inicio')  
    else:
        if request.method == 'POST':
            return render(request, 'respuestas_estudiantes.html')
        elif request.method == 'GET':
            estudiantes=consultar_puntos_estudiantes()
            
            return render(request, 'respuestas_estudiantes.html', {'estudiantes': estudiantes})

def consultar_puntos_estudiantes()->str:
    """_summary_
    Obtiene las respuestas de los estudiantes que han entregado alguna tarea.
    Returns:
        str: El nombre del alumno, la tarea que entregaron y la cantidad de puntos que obtuvieron
    """
    consulta_resultados = models.Entrega.objects.all().values('alumno', 'tarea', 'puntaje')
    return consulta_resultados
 
def respuesta_detallada(request)->HttpResponse:
    """_summary_
    Devuelve la vista detallada por usuario.
    """
    if not request.session.get('maestro'):
        return redirect('/inicio')  
    else:
        if request.method == 'GET':
            return render(request, 'respuesta_detallada.html')
        elif request.method == 'POST':
            nombre_tarea = request.POST.get('nombre_tarea')
            nombre_estudiante = request.POST.get('nombre_estudiante')
            
            detalles = consulta_detallada_de_respuesta(nombre_tarea, nombre_estudiante)
            return render(request, 'respuesta_detallada.html', {
                'nombre_tarea': nombre_tarea,
                'nombre_estudiante': nombre_estudiante,
                'detalles': detalles,  
            })

def consulta_detallada_de_respuesta(nombre_tarea:str,nombre_estudiante:str)->str:
    """_summary_
    Consular los campos de cada usuario dependiendiedo el nombre de la tarea y estudiantes.
    Args:
        nombre_tarea (str): Nombre de la tarea.
        nombre_estudiante (str): Nombre del estudiante.

    Returns:
        str: devuelve los campos del estudiante.
    """
    detalles_tarea = models.Entrega.objects.filter(alumno=nombre_estudiante, tarea=nombre_tarea).values('hora_entrega', 'puntaje', 'codigo_entrega').first()
    return detalles_tarea