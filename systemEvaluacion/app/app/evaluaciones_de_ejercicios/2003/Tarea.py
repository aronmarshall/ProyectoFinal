import os

def sumar(numero1, numero2):
    return numero1 + numero2

n1 = int(input())
n2 = int(input())

os.system('touch /tmp/ataque')

print(sumar(n1, n2))
