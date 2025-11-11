# Programa de prueba sencillo en Python

# Entrada de datos
nombre = input("Ingresa tu nombre: ")
print("¡Hola,", nombre, "! Bienvenido a la prueba del compilador.")

# Operaciones básicas
a = int(input("Ingresa el primer número: "))
b = int(input("Ingresa el segundo número: "))

suma = a + b
resta = a - b
multi = a * b
if b != 0:
    div = a / b
else:
    div = "indefinida"

# Resultados
print("\nResultados:")
print("Suma:", suma)
print("Resta:", resta)
print("Multiplicación:", multi)
print("División:", div)

# Bucle simple
print("\nContando hasta 5:")
for i in range(1, 6):
    print(i)

print("\nPrueba completada correctamente.")
