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
