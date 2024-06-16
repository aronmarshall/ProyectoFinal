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

def listar_tareas_disponibles(request):
    if request.session.get('maestro'):
        return redirect('/inicio_maestro')
    else:
        if request.method == 'GET':
            return render(request, 'tareas_disponibles.html')
        elif request.method == 'POST':        
            return render(request, 'tareas_disponibles.html')






