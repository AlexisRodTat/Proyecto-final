# Programa de prueba intermedio en Python (sin funciones)

print("=== PROGRAMA DE PRUEBA DEL COMPILADOR ===")

nombre = input("Ingresa tu nombre: ")
print(f"\n¡Hola, {nombre}! Bienvenido a la prueba del compilador.\n")

opcion = ""

while opcion != "3":
    print("\nMenú de opciones:")
    print("1. Realizar operaciones básicas")
    print("2. Contar hasta 5")
    print("3. Salir")

    opcion = input("Elige una opción (1-3): ")

    if opcion == "1":
        a = int(input("\nIngresa el primer número: "))
        b = int(input("Ingresa el segundo número: "))

        suma = a + b
        resta = a - b
        multi = a * b
        div = a / b if b != 0 else "indefinida"

        print("\n--- Resultados ---")
        print("Suma:", suma)
        print("Resta:", resta)
        print("Multiplicación:", multi)
        print("División:", div)

        if suma > 10:
            print("La suma es mayor que 10.")
        elif suma == 10:
            print("La suma es igual a 10.")
        else:
            print("La suma es menor que 10.")

    elif opcion == "2":
        print("\nContando hasta 5:")
        for i in range(1, 6):
            print(i)

    elif opcion == "3":
        print("\nGracias por usar el programa. ¡Hasta luego!")

    else:
        print("\nOpción no válida. Intenta de nuevo.")

# Programa de prueba con funciones y clases

print("=== PRUEBA DE FUNCIONES Y CLASES ===")
print()

# ===== PRUEBA DE FUNCIONES =====
print("--- Prueba de Funciones ---")

def saludar(nombre):
    print("¡Hola,", nombre, "!")
    return "Saludo completado"

def sumar(a, b):
    resultado = a + b
    return resultado

def calcular_doble(x):
    return x * 2

# Llamadas a funciones
mensaje = saludar("María")
print("Retorno de saludar:", mensaje)
print()

suma_resultado = sumar(5, 3)
print("5 + 3 =", suma_resultado)

doble = calcular_doble(7)
print("El doble de 7 es:", doble)
print()

# ===== PRUEBA DE CLASES =====
print("--- Prueba de Clases ---")

class Persona:
    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad
    
    def presentarse(self):
        print("Me llamo", self.nombre, "y tengo", self.edad, "años")
        return self.nombre
    
    def cumplir_anios(self):
        self.edad = self.edad + 1
        print(self.nombre, "ahora tiene", self.edad, "años")

# Crear instancias
persona1 = Persona("Juan", 25)
persona2 = Persona("Ana", 30)

# Llamar métodos
persona1.presentarse()
persona2.presentarse()
print()

# Modificar estado
persona1.cumplir_anios()
print()

# ===== CLASE CONTADOR =====
print("--- Clase Contador ---")

class Contador:
    def __init__(self, valor_inicial):
        self.valor = valor_inicial
    
    def incrementar(self):
        self.valor = self.valor + 1
        return self.valor
    
    def obtener_valor(self):
        return self.valor

contador = Contador(0)
print("Valor inicial:", contador.obtener_valor())

contador.incrementar()
print("Después de incrementar:", contador.obtener_valor())

contador.incrementar()
contador.incrementar()
print("Después de 2 incrementos más:", contador.obtener_valor())
print()

print("=== PRUEBA COMPLETADA ===")