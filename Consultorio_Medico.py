import pymongo
from datetime import datetime, timedelta
import re
import json
import os

# Funciones de conexión y manejo de MongoDB
def establecer_conexion():
    try:
        client = pymongo.MongoClient("mongodb://unnoba:12345@localhost:27017/")
        db = client["Consultorio_medico"]
        collection = db["Turnos"]
        print("Conexión a MongoDB establecida correctamente.")
        return collection
    except pymongo.errors.ConnectionFailure:
        print("No se pudo conectar a MongoDB. Guardando datos temporalmente en archivo.")
        return None

# Guardar turnos en archivo temporal
def guardar_turno_temporal(turno):
    with open("turnos_temporales.txt", "a") as file:
        file.write(json.dumps(turno) + "\n")

# Cargar turnos desde archivo temporal
def cargar_turnos_temporales():
    turnos = []
    if os.path.exists("turnos_temporales.txt"):
        with open("turnos_temporales.txt", "r") as file:
            for line in file:
                turnos.append(json.loads(line))
    else:
        with open("turnos_temporales.txt", "w") as file:
            pass
    return turnos

# Guardar turnos solapados
def guardar_turno_solapado(turno):
    with open("turnos_solapados.txt", "a") as file:
        file.write(json.dumps(turno) + "\n")

# Transferir turnos temporales a MongoDB
def transferir_turnos_temporales(collection):
    turnos_temporales = cargar_turnos_temporales()
    if not turnos_temporales:
        print("No hay turnos temporales para transferir.")
        return
    
    exito_transferencia = True
    
    for turno in turnos_temporales:
        existing_turno = collection.find_one({"fecha": turno["fecha"], "hora": turno["hora"]})
        if existing_turno:
            guardar_turno_solapado(turno)
        else:
            collection.insert_one(turno)
            exito_transferencia = False  # Indicar que al menos un turno no se pudo transferir
    
    if exito_transferencia:
        os.remove("turnos_temporales.txt")
        print("Turnos temporales transferidos a MongoDB y archivo temporal eliminado.")
    else:
        print("Algunos turnos temporales no se pudieron transferir completamente a MongoDB.")

# Funciones para operaciones con MongoDB
def inicializar_turnos(collection):
    # Limpiar turnos antiguos
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    collection.delete_many({"fecha": {"$lt": fecha_hoy}})
    
    # Agregar nuevos turnos si es necesario
    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    hora_inicio = datetime.strptime("09:00", "%H:%M")

    turnos = []
    fecha_inicio = datetime.now()
    fecha_limite = fecha_inicio + timedelta(days=14)
    
    while fecha_inicio <= fecha_limite:
        fecha_str = fecha_inicio.strftime("%Y-%m-%d")
        dia_semana = dias_semana[fecha_inicio.weekday() % len(dias_semana)]
        
        if collection.count_documents({"fecha": fecha_str}) == 0:  # Solo agregar si no existen turnos para esa fecha
            for j in range(30):
                hora_turno = (hora_inicio + timedelta(minutes=20 * j)).strftime("%H:%M")
                turnos.append({
                    "fecha": fecha_str,
                    "dia": dia_semana,
                    "hora": hora_turno,
                    "ocupado": False,
                    "nombre": None,
                    "apellido": None,
                    "dni": None,
                    "mutual": None
                })
        fecha_inicio += timedelta(days=1)

    if turnos:
        collection.insert_many(turnos)
        print("Turnos nuevos inicializados correctamente.")
    else:
        print("No se necesitan inicializar nuevos turnos.")

# Funciones de validación
def validar_fecha(fecha):
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validar_hora(hora):
    if re.match(r"^\d{2}:\d{2}$", hora):
        try:
            datetime.strptime(hora, "%H:%M")
            return True
        except ValueError:
            return False
    return False

def validar_nombre_apellido(texto):
    return texto.isalpha()

def validar_dni(dni):
    return dni.isdigit()

# Funciones para operaciones con turnos
def asignar_turno(collection, fecha, hora):
    nombre = input("Ingrese el nombre: ")
    while not validar_nombre_apellido(nombre):
        print("Error: El nombre no puede contener números.")
        nombre = input("Ingrese el nombre nuevamente: ")

    apellido = input("Ingrese el apellido: ")
    while not validar_nombre_apellido(apellido):
        print("Error: El apellido no puede contener números.")
        apellido = input("Ingrese el apellido nuevamente: ")

    dni = input("Ingrese el DNI: ")
    while not validar_dni(dni):
        print("Error: El DNI debe ser numérico.")
        dni = input("Ingrese el DNI nuevamente: ")

    mutual = None
    tiene_mutual = input("¿Tiene mutual (obra social)? (s/n): ").lower()
    if tiene_mutual == 's':
        mutual = input("Ingrese el nombre de la mutual: ")

    turno = {
        "fecha": fecha,
        "hora": hora,
        "ocupado": True,
        "nombre": nombre,
        "apellido": apellido,
        "dni": dni,
        "mutual": mutual
    }
    
    if collection is not None:
        existing_turno = collection.find_one({"fecha": fecha, "hora": hora})
        if existing_turno and existing_turno["ocupado"]:
            print("¡El turno para esa fecha ya está ocupado!")
        else:
            collection.update_one(
                {"fecha": fecha, "hora": hora},
                {"$set": turno},
                upsert=True
            )
            print(f"Turno asignado correctamente para la fecha: {fecha} a las {hora}.")
    else:
        guardar_turno_temporal(turno)
        print(f"Turno guardado temporalmente para la fecha: {fecha} a las {hora}.")

def cancelar_turno(collection, fecha, hora):
    if collection is not None:
        turno = collection.find_one({"fecha": fecha, "hora": hora, "ocupado": True})
        if turno:
            collection.update_one(
                {"fecha": fecha, "hora": hora},
                {"$set": {"ocupado": False, "nombre": None, "apellido": None, "dni": None, "mutual": None}}
            )
            print(f"Turno cancelado correctamente para la fecha: {fecha} a las {hora}.")
        else:
            print("No se encontró un turno para esa fecha y hora.")
    else:
        print("No se puede cancelar el turno porque no hay conexión a MongoDB.")

def mostrar_turnos_ocupados(collection):
    if collection is not None:
        turnos_ocupados = collection.find({"ocupado": True}).sort([("fecha", pymongo.ASCENDING), ("hora", pymongo.ASCENDING)])
        print("Turnos ocupados:")
        for turno in turnos_ocupados:
            nombre_apellido = f"{turno['nombre']} {turno['apellido']}"
            mutual = turno.get('mutual', 'No tiene')
            print(f"Fecha: {turno['fecha']} - Hora: {turno['hora']} - Paciente: {nombre_apellido} - Mutual: {mutual}")
    else:
        print("No se puede mostrar turnos ocupados porque no hay conexión a MongoDB.")

def mostrar_turnos_disponibles(collection):
    dia = input("Ingrese el día de la semana que le interesa: ")
    fecha = input("Ingrese la fecha (formato YYYY-MM-DD): ")
    
    if not validar_fecha(fecha):
        print("Error: Fecha inválida. Por favor, ingrese la fecha en el formato YYYY-MM-DD.")
        return

    if collection is not None:
        turnos_disponibles = collection.find({
            "dia": dia,
            "fecha": fecha,
            "ocupado": False
        }).sort("hora", pymongo.ASCENDING)

        print(f"Turnos disponibles para {dia}, {fecha}:")
        for turno in turnos_disponibles:
            print(f"Fecha: {turno['fecha']} - Hora: {turno['hora']}")
    else:
        print("No se puede mostrar turnos disponibles porque no hay conexión a MongoDB.")

def mostrar_turnos_mutual(collection):
    if collection is not None:
        turnos_con_mutual = collection.find({"ocupado": True, "mutual": {"$ne": None}}).sort([("fecha", pymongo.ASCENDING), ("hora", pymongo.ASCENDING)])
        print("Turnos con mutual:")
        for turno in turnos_con_mutual:
            nombre_apellido = f"{turno['nombre']} {turno['apellido']}"
            mutual = turno['mutual']
            print(f"Fecha: {turno['fecha']} - Hora: {turno['hora']} - Paciente: {nombre_apellido} - Mutual: {mutual}")
    else:
        print("No se puede mostrar turnos con mutual porque no hay conexión a MongoDB.")

# Programa principal
if __name__ == "__main__":
    collection = establecer_conexion()

    if collection is not None:
        inicializar_turnos(collection)
        transferir_turnos_temporales(collection)

        while True:
            print("\nOpciones:")
            print("1. Asignar un nuevo turno")
            print("2. Cancelar un turno")
            print("3. Mostrar turnos ocupados")
            print("4. Mostrar turnos con mutual")
            print("5. Mostrar turnos disponibles")
            print("6. Salir")

            opcion = input("Seleccione una opción (1-6): ")

            if opcion == "1":
                while True:
                    fecha = input("Ingrese la fecha (formato YYYY-MM-DD): ")
                    if not validar_fecha(fecha):
                        print("Error: Fecha inválida. Por favor, ingrese la fecha en el formato YYYY-MM-DD.")
                        continue
                    
                    hora = input("Ingrese la hora (formato HH:MM): ")
                    if not validar_hora(hora):
                        print("Error: Hora inválida. Por favor, ingrese la hora en el formato HH:MM.")
                        continue
                    
                    asignar_turno(collection, fecha, hora)
                    break
                
            elif opcion == "2":
                while True:
                    fecha = input("Ingrese la fecha (formato YYYY-MM-DD): ")
                    if not validar_fecha(fecha):
                        print("Error: Fecha inválida. Por favor, ingrese la fecha en el formato YYYY-MM-DD.")
                        continue
                    
                    hora = input("Ingrese la hora del turno a cancelar (formato HH:MM): ")
                    if not validar_hora(hora):
                        print("Error: Hora inválida. Por favor, ingrese la hora en el formato HH:MM.")
                        continue
                    
                    cancelar_turno(collection, fecha, hora)
                    break
                
            elif opcion == "3":
                mostrar_turnos_ocupados(collection)
            
            elif opcion == "4":
                mostrar_turnos_mutual(collection)

            elif opcion == "5":
                mostrar_turnos_disponibles(collection)
            
            elif opcion == "6":
                break
            
            else:
                print("Opción no válida. Por favor, intente de nuevo.")
    else:
        print("No se pudo establecer conexión con MongoDB. El programa finalizará.")