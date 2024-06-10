import pymongo
from datetime import datetime, timedelta

# Conectarse a MongoDB (hay que tener MongoDB abierto de manera local)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Consultorio_medico"] #servidor
collection = db["Turnos"]

# Inicializar la colección Turnos
def inicializar_turnos():
    collection.delete_many({})  # Limpiar la colección existente si hay datos previos

    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    hora_inicio = datetime.strptime("09:00", "%H:%M")

    turnos = []
    fecha_inicio = datetime.now()
    for i in range(0, 15):  # Dos semanas de turnos
        fecha = (fecha_inicio + timedelta(days=i))
        dia_semana = dias_semana[fecha.weekday() % len(dias_semana)]
        for j in range(30):
            hora_turno = (hora_inicio + timedelta(minutes=20 * j)).strftime("%H:%M")
            turnos.append({
                "fecha": fecha.strftime("%Y-%m-%d"),
                "dia": dia_semana,
                "hora": hora_turno,
                "ocupado": False,
                "nombre": None,
                "apellido": None,
                "dni": None
            })

    collection.insert_many(turnos)
    print("Turnos inicializados correctamente.")

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

###############################################################################################################
###############################################################################################################






# Función para mostrar turnos disponibles
def mostrar_turnos_disponibles():
    fecha_actual = datetime.now().strftime("%Y-%m-%d")
    fecha_limite = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    
    dia = input("Ingrese el día de la semana que le interesa: ")
    fecha = input("Ingrese la fecha (formato YYYY-MM-DD): ")

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
            fecha = input("Ingrese la fecha (formato YYYY-MM-DD): ")
            hora = input("Ingrese la hora (formato HH:MM): ")
            nombre = input("Ingrese el nombre: ")
            apellido = input("Ingrese el apellido: ")
            dni = input("Ingrese el DNI: ")
            asignar_turno(fecha, hora, nombre, apellido, dni)
        elif opcion == "2":
            fecha = input("Ingrese la fecha (formato YYYY-MM-DD): ")
            hora = input("Ingrese la hora del turno a cancelar (formato HH:MM): ")
            cancelar_turno(fecha, hora)
        elif opcion == "3":
            mostrar_turnos_ocupados()
        elif opcion == "4":
            mostrar_turnos_disponibles()
        elif opcion == "5":
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")