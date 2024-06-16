from django.db import models

# Create your models here.
from django.db import models

# Create your models here.

class Alumno(models.Model):
    nombre_completo = models.CharField(max_length=35)
    matricula = models.CharField(max_length=10, unique=True)

class Usuario(models.Model):
    idRegistro = models.AutoField(primary_key=True)
    usuario = models.CharField(max_length=20)
    contrasenia = models.BinaryField(max_length=64)
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, null=True, blank=True)


class TelegramData(models.Model):
    id_token = models.AutoField(primary_key=True)
    usuario = models.CharField(max_length=20)
    usuarioTelegram = models.CharField(max_length=40, null=False)
    tokens = models.CharField(max_length=6)
    tiempo = models.TimeField()
    enviar = models.BooleanField(default=True)

class Intentos(models.Model):
    ip = models.GenericIPAddressField(primary_key=True)
    intentos = models.PositiveIntegerField()
    fecha_ultimo_intento = models.DateTimeField()

class crear_tarea(models.Model):
    id_tarea = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion_general = models.TextField()
    entrada_esperada = models.CharField(max_length=255)
    salida_esperada = models.CharField(max_length=255)
    archivo_evaluar = models.FileField(upload_to='documentos/', null=True, default=None)