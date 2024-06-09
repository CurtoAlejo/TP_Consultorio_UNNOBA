import pymongo

#Conectarse a MongoDB (hay que tener MongoDB en abierto de manera local)
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["Consultorio_medico"]
collection = db["Turnos"] #Los clietnes y las colecciones tiene q ser las mismas para q ande, claramente

def asignar_turno(nombre, apellido, dni, fecha):
    # Verificar si el turno solicitado ya está ocupado
    if collection.find_one({"fecha": fecha}):
        print("¡El turno para esa fecha ya está ocupado!")
    else:
        turno = {"nombre": nombre, "apellido": apellido, "dni": dni, "fecha": fecha}
        collection.insert_one(turno)
        print("Turno asignado correctamente.")

def cancelar_turno(fecha):
    # Verificar si el turno a cancelar existe
    turno = collection.find_one({"fecha": fecha})
    if turno:
        collection.delete_one({"fecha": fecha})
        print("Turno cancelado correctamente.")
    else:
        print("No se encontró un turno para esa fecha.")

def mostrar_turnos_disponibles():
    # Mostrar todos los turnos disponibles ordenados por fecha
    turnos_disponibles = collection.find().sort("fecha", pymongo.ASCENDING)
    print("Turnos disponibles:")
    for turno in turnos_disponibles:
        print(f"Fecha: {turno['fecha']} - Paciente: {turno['nombre']} {turno['apellido']}")