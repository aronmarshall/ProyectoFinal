from django.shortcuts import render, redirect



def crear_tarea(request):

    return render(request, 'crear_tarea.html')

def listar_mis_tareas(request):

    return render(request, 'listar_mis_tareas.html')
    
def respuestas_estudiantes(request):

    return render(request, 'listar_mis_tareas.html')