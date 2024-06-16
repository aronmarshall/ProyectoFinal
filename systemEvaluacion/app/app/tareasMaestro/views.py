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


def crear_tarea(request):
    if not request.session.get('maestro'):
        return redirect('/inicio')
    else:
        if request.method == 'GET':
            return render(request, 'crear_tarea.html')
        elif request.method == 'POST':
            cadena_numeros = nrc()
            id_tarea=cadena_numeros
            nombre_eje = request.POST.get('nombre_eje')
            descripcion = request.POST.get('descripcion')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_cierre = request.POST.get('fecha_cierre')
            entrada = request.POST.get('entrada')
            salida = request.POST.get('salida')
            salida_ejemplo = request.FILES.get('salida_ejemplo')

            insertar_datos = models.crear_tarea(id_tarea=id_tarea, nombre=nombre_eje, descripcion_general=descripcion, 
                fecha_inicio=fecha_inicio, fecha_cierre=fecha_cierre, entrada_esperada=entrada, 
                salida_esperada=salida, archivo_evaluar=salida_ejemplo)
            insertar_datos.save()

            messages.info(request, f'Se inserto la actividad {nombre_eje}')
            return render(request, 'inicio_maestro.html')

def nrc():
    return ''.join(str(random.randint(0, 9)) for _ in range(4))

def listar_mis_tareas(request):
    if not request.session.get('maestro'):
        return redirect('/inicio')
    else:
        if request.method == 'POST':
            return render(request, 'listar_mis_tareas.html')
        elif request.method == 'GET':
            consultar_mis_tareas = models.crear_tarea.objects.all()
            messages.info(request, f'Se encontraron {consultar_mis_tareas.count()} tareas.')
            return render(request, 'listar_mis_tareas.html', {'tareas': consultar_mis_tareas})

def eliminar_tareas(request):
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
                    tarea = models.crear_tarea.objects.get(id_tarea=eliminar_numero)
                    tarea.delete()
                    messages.success(request, f'Tarea "{tarea.nombre}" eliminada correctamente.')            
                    return redirect('/listar_mis_tareas')
                except models.crear_tarea.DoesNotExist:
                    messages.error(request, f'La tarea "{eliminar_numero}" no existe.')
                    return redirect('/listar_mis_tareas')

def existe_ejercicio(eliminar):
    existe=models.crear_tarea.objects.filter(id_tarea=eliminar).exists()
    if existe:
        return True
    else:
        return False

def respuestas_estudiantes(request):
    if not request.session.get('maestro'):
        return redirect('/inicio')
    else:
        return render(request, 'listar_mis_tareas.html')