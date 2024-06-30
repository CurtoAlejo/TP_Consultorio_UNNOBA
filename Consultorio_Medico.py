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
                    "dni": None,
                    "mutual": None  # Nuevo campo para la mutual
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

# Función para validar que no haya números en nombre o apellido
def validar_nombre_apellido(texto):
    return texto.isalpha()

# Función para validar que el DNI sea numérico
def validar_dni(dni):
    return dni.isdigit()

# Función para asignar un turno
def asignar_turno(fecha, hora):
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

    turno = collection.find_one({"fecha": fecha, "hora": hora})
    if turno and turno["ocupado"]:
        print("¡El turno para esa fecha ya está ocupado!")
    else:
        collection.update_one(
            {"fecha": fecha, "hora": hora},
            {"$set": {"ocupado": True, "nombre": nombre, "apellido": apellido, "dni": dni, "mutual": mutual}}
        )
        print(f"Turno asignado correctamente para la fecha: {fecha} a las {hora}.")

# Función para cancelar un turno
def cancelar_turno(fecha, hora):
    turno = collection.find_one({"fecha": fecha, "hora": hora, "ocupado": True})
    if turno:
        collection.update_one(
            {"fecha": fecha, "hora": hora},
            {"$set": {"ocupado": False, "nombre": None, "apellido": None, "dni": None, "mutual": None}}
        )
        print(f"Turno cancelado correctamente para la fecha: {fecha} a las {hora}.")
    else:
        print("No se encontró un turno para esa fecha y hora.")

# Función para mostrar turnos ocupados
def mostrar_turnos_ocupados():
    turnos_ocupados = collection.find({"ocupado": True}).sort([("fecha", pymongo.ASCENDING), ("hora", pymongo.ASCENDING)])
    print("Turnos ocupados:")
    for turno in turnos_ocupados:
        nombre_apellido = f"{turno['nombre']} {turno['apellido']}"
        if 'mutual' in turno:
            mutual = turno['mutual']
        else:
            mutual = 'No tiene'
        print(f"Fecha: {turno['fecha']} - Hora: {turno['hora']} - Paciente: {nombre_apellido} - Mutual: {mutual}")

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

# Función para mostrar turnos con mutual
def mostrar_turnos_mutual():
    turnos_con_mutual = collection.find({"ocupado": True, "mutual": {"$ne": None}}).sort([("fecha", pymongo.ASCENDING), ("hora", pymongo.ASCENDING)])
    print("Turnos con mutual:")
    for turno in turnos_con_mutual:
        print(f"Fecha: {turno['fecha']} - Hora: {turno['hora']} - Paciente: {turno['nombre']} {turno['apellido']} - Mutual: {turno['mutual']}")

# Inicializar turnos si es necesario
inicializar_turnos()

# Ejemplo de uso
if __name__ == "__main__":
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
                
                asignar_turno(fecha, hora)
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
                
                cancelar_turno(fecha, hora)
                break
            
        elif opcion == "3":
            mostrar_turnos_ocupados()
        
        elif opcion == "4":
            mostrar_turnos_mutual()

        elif opcion == "5":
            mostrar_turnos_disponibles()
        
        elif opcion == "6":
            break
        
        else:
            print("Opción no válida. Por favor, intente de nuevo.")