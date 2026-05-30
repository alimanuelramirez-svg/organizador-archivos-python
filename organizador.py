import os
import shutil

# 1. Definir la ruta de la carpeta que queremos organizar.
# En este caso, usaremos la carpeta de prueba que acabamos de crear.
CARPETA_A_ORGANIZAR = "CarpetaPrueba"

# 2. Definir las categorías y sus extensiones correspondientes.
# Este diccionario mapea el nombre de la carpeta destino a una lista de extensiones.
DICCIONARIO_EXTENSIONES = {
    "Documentos": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv"],
    "Imagenes": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Audio": [".mp3", ".wav", ".flac", ".m4a"],
    "Comprimidos": [".zip", ".rar", ".tar", ".gz", ".7z"],
    "Instaladores": [".exe", ".msi"]
}

def organizar_carpeta(ruta_carpeta):
    # Verificar si la carpeta existe
    if not os.path.exists(ruta_carpeta):
        print(f"Error: La carpeta '{ruta_carpeta}' no existe.")
        return

    print(f"Iniciando la organización de la carpeta: {os.path.abspath(ruta_carpeta)}\n")

    # Obtener la lista de todos los elementos dentro de la carpeta
    elementos = os.listdir(ruta_carpeta)
    archivos_movidos = 0

    for elemento in elementos:
        ruta_elemento = os.path.join(ruta_carpeta, elemento)

        # Solo queremos procesar archivos (no carpetas)
        if os.path.isfile(ruta_elemento):
            # Ignoramos el script organizador si estuviera en la misma carpeta
            if elemento == "organizador.py":
                continue

            # Obtener el nombre del archivo y su extensión en minúsculas
            nombre_archivo, extension = os.path.splitext(elemento)
            extension = extension.lower()

            # Buscar a qué categoría pertenece la extensión
            carpeta_destino = "Otros"
            for categoria, extensiones in DICCIONARIO_EXTENSIONES.items():
                if extension in extensiones:
                    carpeta_destino = categoria
                    break

            # Crear la ruta completa para la carpeta de destino
            ruta_carpeta_destino = os.path.join(ruta_carpeta, carpeta_destino)

            # Crear la carpeta de destino si no existe
            if not os.path.exists(ruta_carpeta_destino):
                os.makedirs(ruta_carpeta_destino)
                print(f"Creada la carpeta: {carpeta_destino}")

            # Definir la ruta de destino final del archivo
            ruta_destino_final = os.path.join(ruta_carpeta_destino, elemento)

            try:
                # Mover el archivo
                shutil.move(ruta_elemento, ruta_destino_final)
                print(f"Movido: '{elemento}' -> {carpeta_destino}/")
                archivos_movidos += 1
            except Exception as e:
                print(f"No se pudo mover '{elemento}': {e}")

    print(f"\n¡Organización completada! Se movieron {archivos_movidos} archivos.")

if __name__ == "__main__":
    organizar_carpeta(CARPETA_A_ORGANIZAR)
