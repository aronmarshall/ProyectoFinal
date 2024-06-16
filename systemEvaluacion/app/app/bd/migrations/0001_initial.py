# Generated by Django 4.2.11 on 2024-06-16 08:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Alumno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_completo', models.CharField(max_length=35)),
                ('matricula', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='crear_tarea',
            fields=[
                ('id_tarea', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255)),
                ('descripcion_general', models.TextField()),
                ('fecha_inicio', models.DateField()),
                ('fecha_cierre', models.DateField()),
                ('entrada_esperada', models.CharField(max_length=255)),
                ('salida_esperada', models.CharField(max_length=255)),
                ('archivo_evaluar', models.FileField(default=None, null=True, upload_to='documentos/')),
            ],
        ),
        migrations.CreateModel(
            name='Intentos',
            fields=[
                ('ip', models.GenericIPAddressField(primary_key=True, serialize=False)),
                ('intentos', models.PositiveIntegerField()),
                ('fecha_ultimo_intento', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='TelegramData',
            fields=[
                ('id_token', models.AutoField(primary_key=True, serialize=False)),
                ('usuario', models.CharField(max_length=20)),
                ('usuarioTelegram', models.CharField(max_length=40)),
                ('tokens', models.CharField(max_length=6)),
                ('tiempo', models.TimeField()),
                ('enviar', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('idRegistro', models.AutoField(primary_key=True, serialize=False)),
                ('usuario', models.CharField(max_length=20)),
                ('contrasenia', models.BinaryField(max_length=64)),
                ('alumno', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bd.alumno')),
            ],
        ),
    ]
