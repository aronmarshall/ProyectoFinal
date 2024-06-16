from pyexpat.errors import messages
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from datetime import datetime, timezone, date

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


def listar_tareas_disponibles(request):
    if request.session.get('maestro'):
        return redirect('/inicio_maestro')
    else:
        if request.method == 'GET':
            hoy = fecha_actual()
            tareas_validas = obtener_tareas_con_estado(hoy)
            
            messages.info(request, f'Fecha: {hoy}')
            return render(request, 'tareas_disponibles.html', {'tareas_validas': tareas_validas})   
        elif request.method == 'POST':
            return render(request, 'tareas_disponibles.html')

def fecha_valida(fecha_inicio):
    hoy = date.today()
    return fecha_inicio >= hoy and fecha_inicio <= hoy 

def fecha_actual() -> date:
    return date.today()

def obtener_tareas_con_estado(hoy: date):
    tareas_validas = validar_tareas_por_fecha(hoy)
    tareas_con_estado = []

    for tarea in models.crear_tarea.objects.all():
        tarea.estado_valido = fecha_valida(tarea.fecha_inicio)
        tareas_con_estado.append(tarea)
    return tareas_con_estado

def validar_tareas_por_fecha(hoy: date):
    return models.crear_tarea.objects.filter(fecha_inicio__lte=hoy, fecha_cierre__gte=hoy)
