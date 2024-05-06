import os

activado = ''
with os.popen('ccdecrypt -c secrets.env.cpt') as file: 
    for line in file:
        activado = '1'
        key, value = line.strip().split('=')
        os.environ[key] = value

if not activado:
    print("No se pasó correctamente la contraseña")
    exit(1)

os.system('python3 manage.py runserver 0.0.0.0:8000')
os.system('python3 manage.py makemigrations')
os.system('python3 manage.py migrate')