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
import struct

def crear_tarea(request):
    if request.method == 'GET':
        return render(request, 'crear_tarea.html')
    elif request.method == 'POST':
        id_tarea=90
        nombre_eje = request.POST.get('nombre_eje')
        descripcion = request.POST.get('descripcion')
        entrada = request.POST.get('entrada')
        salida = request.POST.get('salida')
        salida_ejemplo = request.FILES.get('salida_ejemplo')

        insertar_datos = models.crear_tarea(id_tarea=id_tarea, nombre=nombre_eje, descripcion_general=descripcion, 
            entrada_esperada=entrada, salida_esperada=salida, archivo_evaluar=salida_ejemplo)
        insertar_datos.save()

        messages.info(request, f'Se inserto.{insertar_datos}')
        return render(request, 'crear_tarea.html')

def aleatoria(vueltas: int) -> str:
    resultados = []
    for _ in range(vueltas):
        p = os.urandom(8)  # Generamos 8 bytes para obtener un número entero de 64 bits
        valor_nrc = struct.unpack('<Q', p)[0]  # Desempaquetamos los bytes como un entero sin signo de 64 bits
        resultados.append(valor_nrc)
    return resultados

def nrc_tarea():
    numeroVueltas=random.randint(1, 5)
    nrc=aleatoria(numeroVueltas)
    return nrc

def listar_mis_tareas(request):
    if request.method == 'POST':
        return render(request, 'listar_mis_tareas.html')
    elif request.method == 'GET':
        consultar_mis_tareas = models.crear_tarea.objects.all()
        messages.info(request, f'Se encontraron {consultar_mis_tareas.count()} tareas.')
        return render(request, 'listar_mis_tareas.html', {'tareas': consultar_mis_tareas})

def eliminar_tareas(request):
    if request.method == 'GET':
        return render(request, 'listar_mis_tareas.html')
    elif request.method == 'POST':
        eliminar = request.POST.get('elimina_tarea')
        tarea = models.crear_tarea.objects.get(nombre=elimina_tarea)
        tarea.delete()
        messages.success(request, f'Tarea "{tarea.nombre}" eliminada correctamente.')
        return redirect('listar_mis_tareas')

def respuestas_estudiantes(request):

    return render(request, 'listar_mis_tareas.html')