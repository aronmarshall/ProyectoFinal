from django.db import models

# Create your models here.

class Intentos(models.Model):
    ip = models.GenericIPAddressField(primary_key=True)
    intentos = models.PositiveIntegerField()
    fecha_ultimo_intento = models.DateTimeField()
    
class Alumno(models.Model):
    nombre_completo = models.CharField(max_length=35)
    matricula = models.CharField(max_length=10, unique=True)

class Usuario(models.Model):
    idRegistro = models.AutoField(primary_key=True)
    usuario = models.CharField(max_length=20)
    contrasenia = models.BinaryField(max_length=64)
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)