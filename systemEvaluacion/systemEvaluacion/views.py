from pyexpat.errors import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from datetime import datetime
from datetime import timezone
from bd import models
from systemEvaluacion import settings

def inicio(request):
    return render(request, 'inicio.html')

def registro_de_usuario(request):
    if request.method == 'POST':
        nombre_completo = request.POST.get('nombre_completo')
        matricula = request.POST.get('matricula')
        usuario = request.POST.get('usuario_nuevo')
        contrasenia = request.POST.get('contrasenia')

        
        nuevo_alumno = models.Alumno(nombre_completo=nombre_completo, matricula=matricula)
        nuevo_alumno.save()
        id_alumno = nuevo_alumno.id

        # Crear un nuevo usuario relacionado con el alumno
        nuevo_usuario = models.Usuario(usuario=usuario, contrasenia=contrasenia.encode(), alumno_id=id_alumno)
        nuevo_usuario.save()

        return redirect('autenticacion.html')
    return render(request, 'registro.html')