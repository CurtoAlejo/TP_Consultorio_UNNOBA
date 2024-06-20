import pymongo
from datetime import datetime, timedelta
import re

# Conectarse a MongoDB (hay que tener MongoDB abierto de manera local)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Consultorio_medico"]  # servidor
collection = db["Turnos"]

# Inicializar la colección Turnos si está vacía
def inicializar_turnos():
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
                    "dni": None
                })
        fecha_inicio += timedelta(days=1)

    if turnos:
        collection.insert_many(turnos)
        print("Turnos nuevos inicializados correctamente.")
    else:
        print("No se necesitan inicializar nuevos turnos.")

# Función para validar fecha
def validar_fecha(fecha):
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        return True
    except ValueError:
        return False

# Función para validar hora
def validar_hora(hora):
    # Verificar el formato exacto HH:MM
    if re.match(r"^\d{2}:\d{2}$", hora):
        try:
            datetime.strptime(hora, "%H:%M")
            return True
        except ValueError:
            return False
    return False

# Función para asignar un turno
def asignar_turno(fecha, hora, nombre, apellido, dni):
    turno = collection.find_one({"fecha": fecha, "hora": hora})
    if turno and turno["ocupado"]:
        print("¡El turno para esa fecha ya está ocupado!")
    else:
        collection.update_one(
            {"fecha": fecha, "hora": hora},
            {"$set": {"ocupado": True, "nombre": nombre, "apellido": apellido, "dni": dni}}
        )
        print(f"Turno asignado correctamente para la fecha: {fecha} a las {hora}.")

# Función para cancelar un turno
def cancelar_turno(fecha, hora):
    turno = collection.find_one({"fecha": fecha, "hora": hora, "ocupado": True})
    if turno:
        collection.update_one(
            {"fecha": fecha, "hora": hora},
            {"$set": {"ocupado": False, "nombre": None, "apellido": None, "dni": None}}
        )
        print(f"Turno cancelado correctamente para la fecha: {fecha} a las {hora}.")
    else:
        print("No se encontró un turno para esa fecha y hora.")

# Función para mostrar turnos ocupados
def mostrar_turnos_ocupados():
    turnos_ocupados = collection.find({"ocupado": True}).sort([("fecha", pymongo.ASCENDING), ("hora", pymongo.ASCENDING)])
    print("Turnos ocupados:")
    for turno in turnos_ocupados:
        print(f"Fecha: {turno['fecha']} - Hora: {turno['hora']} - Paciente: {turno['nombre']} {turno['apellido']}")

# Función para mostrar turnos disponibles
def mostrar_turnos_disponibles():
    dia = input("Ingrese el día de la semana que le interesa: ")
    fecha = input("Ingrese la fecha (formato YYYY-MM-DD): ")
    
    if not validar_fecha(fecha):
        print("Error: Fecha inválida. Por favor, ingrese la fecha en el formato YYYY-MM-DD.")
        return

    turnos_disponibles = collection.find({
        "dia": dia,
        "fecha": fecha,
        "ocupado": False
    }).sort("hora", pymongo.ASCENDING)

    print(f"Turnos disponibles para {dia}, {fecha}:")
    for turno in turnos_disponibles:
        print(f"Fecha: {turno['fecha']} - Hora: {turno['hora']}")

# Inicializar turnos si es necesario
inicializar_turnos()

# Ejemplo de uso
if __name__ == "__main__":
    while True:
        print("\nOpciones:")
        print("1. Asignar un nuevo turno")
        print("2. Cancelar un turno")
        print("3. Mostrar turnos ocupados")
        print("4. Mostrar turnos disponibles")
        print("5. Salir")

        opcion = input("Seleccione una opción (1-5): ")

        if opcion == "1":
            while True:
                fecha = input("Ingrese la fecha (formato YYYY-MM-DD): ")
                if validar_fecha(fecha):
                    break
                print("Error: Fecha inválida. Por favor, ingrese la fecha en el formato YYYY-MM-DD.")
            
            while True:
                hora = input("Ingrese la hora (formato HH:MM): ")
                if validar_hora(hora):
                    break
                print("Error: Hora inválida. Por favor, ingrese la hora en el formato HH:MM.")
            
            nombre = input("Ingrese el nombre: ")
            apellido = input("Ingrese el apellido: ")
            dni = input("Ingrese el DNI: ")
            asignar_turno(fecha, hora, nombre, apellido, dni)
        
        elif opcion == "2":
            while True:
                fecha = input("Ingrese la fecha (formato YYYY-MM-DD): ")
                if validar_fecha(fecha):
                    break
                print("Error: Fecha inválida. Por favor, ingrese la fecha en el formato YYYY-MM-DD.")
            
            while True:
                hora = input("Ingrese la hora del turno a cancelar (formato HH:MM): ")
                if validar_hora(hora):
                    break
                print("Error: Hora inválida. Por favor, ingrese la hora en el formato HH:MM.")
            
            cancelar_turno(fecha, hora)
        
        elif opcion == "3":
            mostrar_turnos_ocupados()
        
        elif opcion == "4":
            mostrar_turnos_disponibles()
        
        elif opcion == "5":
            break
        
        else:
            print("Opción no válida. Por favor, intente de nuevo.")