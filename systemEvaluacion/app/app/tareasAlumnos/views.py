from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from datetime import datetime, date
from django.utils import timezone

from bd import models
from systemEvaluacion import settings

import os
import shutil
import subprocess
import docker

##########################################################Devuelve las tareas disponibles
def listar_tareas_disponibles(request)->HttpResponse:
    """
    Lista las tareas disponibles en función de la sesión del usuario y el método de solicitud.
    
    Args:
        request: Objeto HttpRequest que contiene metadatos sobre la solicitud.
        
    Returns:
        Objeto HttpResponse con la plantilla de tareas renderizada o una respuesta de redirección.
    """
    if request.session.get('maestro'):
        return redirect('/inicio_maestro')  
    else:
        if request.method == 'GET':  
            
            hoy = date.today()  
            tareas_validas = obtener_tareas_con_estado(hoy)  

            messages.info(request, f'Fecha: {hoy}')  
            return render(request, 'tareas_disponibles.html', {'tareas_validas': tareas_validas})
        elif request.method == 'POST':  
            return render(request, 'tareas_disponibles.html')  

def fecha_valida(fecha_inicio:date, fecha_cierre:date)->bool:
    """
    Verifica si la fecha de inicio dada es válida (hoy o posterior).
    
    Args:
        fecha_inicio: Objeto date que representa la fecha de inicio.
        fecha_cierre: Objeto date que representa la fecha de cierre.
    Returns:
        bool: True si la fecha de inicio es válida, False en caso contrario.
    """
    hoy = date.today()  
    return fecha_inicio <= hoy <= fecha_cierre   

def obtener_tareas_con_estado(hoy:date)->list:
    """
    Obtiene las tareas con su estado en función de la fecha actual.
    
    Args:
        hoy: Objeto date que representa la fecha actual.
        
    Returns:
        list: Lista de tareas con su estado.
    """
    tareas_validas = models.Crear_tarea.objects.filter(fecha_inicio__lte=hoy, fecha_cierre__gte=hoy)   
    tareas_con_estado = []  

    for tarea in models.Crear_tarea.objects.all():  
        tarea.estado_valido = fecha_valida(tarea.fecha_inicio, tarea.fecha_cierre)  
        tareas_con_estado.append(tarea)  
    return tareas_con_estado  

##########################################################Muetra detalles de las tareas
def subir_tarea(request)->HttpResponse:
    """
        Permite vizualizar los detalles de la tarea y propociona las entradas del código.
    Args:
        request (_type_): Objeto HttpRequest que contiene metadatos sobre la solicitud.

    Returns:
        HttpResponse: Objeto HttpResponse con la plantilla de tareas renderizada o una respuesta de redirección.
    """
    if request.session.get('maestro'):  
        return redirect('/inicio_maestro')  
    else:
        if request.method == 'GET':  
            return render(request, 'subir_tareas.html')      
        elif request.method == 'POST':  

            nombre_tarea = request.POST.get('nombre_tarea')
            detalles_tarea = consultar_detalles_tarea(nombre_tarea)

            request.session['nombre_entrega_tarea'] = nombre_tarea 
            
            return render(request, 'subir_tareas.html', {'detalles_tarea': detalles_tarea})

def consultar_detalles_tarea(nombre_tarea:str)->str:
    """_summary_
    
    Consulta los detalles por tarea especifica.

    Args:
        nombre_tarea (str): Nombre de la tarea a consultar de manera detallada.

    Returns:
        str: Retorno en forma de Str de los detalles de la tarea.
    """
    try:
        tarea = models.Crear_tarea.objects.get(nombre=nombre_tarea)
        detalles_tarea = {
            'nombre': tarea.nombre,
            'descripcion': tarea.descripcion_general,
            #puntos por obtener posibles
            'fecha_inicio': tarea.fecha_inicio,
            'fecha_cierre': tarea.fecha_cierre,
        }
        return detalles_tarea
    except models.Crear_tarea.DoesNotExist:
        return "No existe la tarea."
##########################################################Entregar la tarea
def entregar_tarea(request)->HttpResponse:
    """
    Es la función que se encarga de insertar los datos por alumno.
    Args:
        request (_type_): Objeto HttpRequest que contiene metadatos sobre la solicitud.

    Returns:
        HttpResponse: Objeto HttpResponse con la plantilla de tareas renderizada o una respuesta de redirección.
    """
    if request.session.get('maestro'):  
        return redirect('/inicio_maestro')  
    else:
        if request.method == 'GET':  
               return render(request, 'inicio.html')      
        elif request.method == 'POST':
            try:
                id_entrega = id_num()
                alumno = request.session.get('alumno')
                tarea = request.session.get('nombre_entrega_tarea')
                hora_entrega = timezone.now()
                puntaje = obtener_puntaje()
                entrega_tarea = request.POST.get('tarea')

                nombre_alumno=consultar_nombre_formal(alumno)
                generar_entorno_de_evaluacion(id_entrega, entrega_tarea, tarea)
                entradas_esperadas(tarea)

                almacenar_tarea = models.Entrega(
                    id_entrega=id_entrega, 
                    alumno=nombre_alumno, 
                    tarea=tarea,
                    hora_entrega=hora_entrega, 
                    puntaje=puntaje, 
                    codigo_entrega=entrega_tarea
                    )
                
                almacenar_tarea.save()
                
                messages.info(request, f'Entregaste la tarea "{tarea}".')
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

def consultar_nombre_formal(alumno:str)->str:
    """
    Pasa el nombre del alumno por el usuario en sesión.
    Args:
        alumno (str): El nombre del usuario en sesión.

    Returns:
        str: devuelve el nombre completo del registro de usuarios.
    """
    usuario = models.Usuario.objects.get(usuario=alumno)
    return usuario.alumno.nombre_completo

##########################################################Crear entorno de archivos 
def generar_entorno_de_evaluacion(id_entrega:int, entrega_tarea:str, tarea:str)->None:
    """
        Genera una ruta por cada entrega del estudiante donde se creara su entorno de evaluación.
    Args:
        id_entrega (int): nuúmero aletorio de la entrega.
        entrega_tarea (str): código de la entrega a evaluar.
        tarea (str): Nombre de la entrega.
    """
    ruta_local = os.getcwd()
    carpeta_de_evaluaciones = "evaluaciones_de_ejercicios"
    directorio_origen='/app/evaluadorBase'  

    ruta_de_eveluacion = os.path.join(ruta_local, carpeta_de_evaluaciones)  
    archivos_a_copiar = os.listdir(directorio_origen)

    try:
        if not os.path.exists(ruta_de_eveluacion):
            os.mkdir(ruta_de_eveluacion)
    except OSErro as e:
        messages.error(request, f'No se puedo crear el ambiente para la evaluación {e}.')

    os.chdir(ruta_de_eveluacion)
    os.mkdir(id_entrega)
    os.chdir(id_entrega)

    directorio_destino=os.getcwd()

    try:
        for archivos in archivos_a_copiar:
            ruta_origen = os.path.join(directorio_origen, archivos)
            ruta_destino = os.path.join(directorio_destino, archivos)
            shutil.copy(ruta_origen, ruta_destino)

        with open('Tarea.py', 'w') as f:
            for linea in entrega_tarea.strip().splitlines():
                f.write(linea + '\n')

            separar_entradas=entradas_esperadas(tarea)
            separar_salidas=salida_esperadas(tarea)
            
            escribir_entrada=separar_entradas.split()
            escribir_salida=separar_salidas.split()

            if len(escribir_entrada) == len(escribir_salida):
                tamanio_lista = len(escribir_entrada)

                with open('Pruebas.txt', 'w') as f:
                    i=0
                    while i < tamanio_lista:
                        f.write(f'{escribir_entrada[i]}\n\n')
                        f.write('!!!!!!\n\n')
                        f.write(f'{escribir_salida[i]}\n\n')
                        f.write('$$$$$$\n\n')
                        i+=1
                crear_docker_file(directorio_destino, id_entrega)
                obtener_puntaje(id_entrega)
            else:
                messages.error(request, f'Las listas no son del mismo tamaño, consulta con tu profesor.')
            
            os.chdir(ruta_local)
    except FileNotFoundError as fnf_error:    
        messages.error(request, f'Error: Archivos no encontrados {fnf_error}')
    except IOError as io_error:
        messages.error(request, f'Error: E/S - {io_error}')        
    except Exception as e:
        messages.error(request, f"Error inesperado - {e}")

def entradas_esperadas(tarea:str)->str:
    """_summary_
    Consulta las entradas esperadas por tarea.
    Args:
        tarea (str): Nombre de la tarea que consultara las entradas.

    Returns:
        str: Devuelve las entradas por tarea.
    """
    entradas = models.Crear_tarea.objects.filter(nombre=tarea).values('entrada_esperada').first()
    if entradas:
        return entradas['entrada_esperada']
    else:
        return None

def salida_esperadas(tarea:str)->str:
    """_summary_
    Consulta las entradas salidas por tarea.
    Args:
        tarea (str): Nombre de la tarea que consultara las salidas.

    Returns:
        str: Devuelve las salidas por tarea.
    """
    salidas = models.Crear_tarea.objects.filter(nombre=tarea).values('salida_esperada').first()
    if salidas:
        return salidas['salida_esperada']
    else:
        return None

##########################################################Obtener Puntaje

def crear_docker_file(directorio_destino:str, id_entrega:int)->None:
    """_summary_
    Crear el docker file para el contenedor.
    Args:
        directorio_destino (str): directorio donde creara el docker file.
        id_entrega (int): es la carpeta donde se ubicara el docker file.
    """
    file = directorio_destino + "/Dockerfile"
    dockerfile = open(file, 'a+')
    dockerfile.write('FROM python:latest\n')
    dockerfile.write(f'WORKDIR /app/evaluaciones_de_ejercicios/{id_entrega}\n')
    dockerfile.write('COPY . .\n')
    dockerfile.write('CMD ["python3", "evaluador.py", "Tarea.py", "Pruebas.txt"]\n')
    dockerfile.close()

def obtener_puntaje(id_entrega:int)->int:
    """_summary_
    Crea un contenedor para ejecutar el programa pasado por el usuario asi con sus casos de prueba
    Args:
        id_entrega (int): es el nombre que se el asignara al contenedor.

    Returns:
        int: La cantidad de True que obtuvo el estudiante.
    """
    num_entrega = str(id_entrega)
    docker_context = f'/app/evaluaciones_de_ejercicios/{id_entrega}'

    client = docker.from_env()
    try:
        image, build_logs = client.images.build(path=docker_context, tag=num_entrega)
        container = client.containers.run(image=num_entrega, detach=True)
        puntaje = container.exec_run(cmd=['python3', 'evaluador.py', 'Tarea.py', 'Pruebas.txt'], stdout=True)
        out = puntaje.output.decode('utf-8').strip()
        
        puntos = out[1:-1]
        contar_puntos = puntos.split(', ')
        contar_aciertos=contar_puntos.count('True')

        container.remove(force=True)
        client.images.remove(image=num_entrega, force=True)

        return contar_aciertos

    except Exception as e:
        messages.error(request, f'Error: {e}')

