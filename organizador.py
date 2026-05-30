import os
import shutil
import tkinter as tk
from tkinter import filedialog, ttk
import subprocess
import threading

# 1. Definir las categorías y sus extensiones correspondientes.
DICCIONARIO_EXTENSIONES = {
    "Documentos": [".pdf", ".docx", ".txt", ".xlsx", ".pptx", ".csv"],
    "Imagenes": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "Audio": [".mp3", ".wav", ".flac", ".m4a"],
    "Comprimidos": [".zip", ".rar", ".tar", ".gz", ".7z"],
    "Instaladores": [".exe", ".msi"]
}

def mostrar_notificacion(titulo, mensaje):
    # Código de PowerShell para mostrar una notificación flotante en Windows
    powershell_code = f"""
    Add-Type -AssemblyName System.Windows.Forms
    $balloon = New-Object System.Windows.Forms.NotifyIcon
    $path = (Get-Process -id $pid).Path
    $balloon.Icon = [System.Drawing.Icon]::ExtractAssociatedIcon($path)
    $balloon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
    $balloon.BalloonTipText = '{mensaje}'
    $balloon.BalloonTipTitle = '{titulo}'
    $balloon.Visible = $true
    $balloon.ShowBalloonTip(5000)
    """
    subprocess.run(["powershell", "-Command", powershell_code], capture_output=True)

def organizar_carpeta(ruta_carpeta, log_callback):
    if not os.path.exists(ruta_carpeta):
        log_callback(f"Error: La carpeta '{ruta_carpeta}' no existe.\n")
        return

    log_callback(f"Iniciando organización en: {ruta_carpeta}\n\n")

    elementos = os.listdir(ruta_carpeta)
    archivos_movidos = 0

    for elemento in elementos:
        ruta_elemento = os.path.join(ruta_carpeta, elemento)

        if os.path.isfile(ruta_elemento):
            # Evitar mover el propio script organizador
            if elemento == "organizador.py":
                continue

            nombre_archivo, extension = os.path.splitext(elemento)
            extension = extension.lower()

            carpeta_destino = "Otros"
            for categoria, extensiones in DICCIONARIO_EXTENSIONES.items():
                if extension in extensiones:
                    carpeta_destino = categoria
                    break

            ruta_carpeta_destino = os.path.join(ruta_carpeta, carpeta_destino)

            if not os.path.exists(ruta_carpeta_destino):
                os.makedirs(ruta_carpeta_destino)
                log_callback(f"Creada la carpeta: {carpeta_destino}\n")

            ruta_destino_final = os.path.join(ruta_carpeta_destino, elemento)

            # Resolución de duplicados
            if os.path.exists(ruta_destino_final):
                nombre_base, ext = os.path.splitext(elemento)
                contador = 1
                while True:
                    nuevo_nombre = f"{nombre_base} ({contador}){ext}"
                    ruta_destino_final = os.path.join(ruta_carpeta_destino, nuevo_nombre)
                    if not os.path.exists(ruta_destino_final):
                        elemento = nuevo_nombre
                        break
                    contador += 1

            try:
                shutil.move(ruta_elemento, ruta_destino_final)
                log_callback(f"Movido: '{elemento}' -> {carpeta_destino}/\n")
                archivos_movidos += 1
            except Exception as e:
                log_callback(f"No se pudo mover '{elemento}': {e}\n")

    log_callback(f"\n¡Organización completada! Se movieron {archivos_movidos} archivos.\n")
    
    # Enviar notificación flotante de Windows
    try:
        if archivos_movidos > 0:
            mostrar_notificacion("Organizador de Archivos", f"¡Completado! Se organizaron {archivos_movidos} archivos.")
        else:
            mostrar_notificacion("Organizador de Archivos", "No se encontraron archivos nuevos para organizar.")
    except Exception:
        # Si las notificaciones de Windows fallan por alguna razón, no detenemos la app
        pass

class OrganizadorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador de Archivos Inteligente 🚀")
        self.root.geometry("620x520")
        self.root.configure(bg="#1e1e2e")  # Fondo oscuro elegante
        self.root.resizable(False, False)

        # Ruta por defecto (Carpeta Descargas del usuario actual)
        self.ruta_actual = tk.StringVar(value=os.path.expanduser("~/Downloads"))

        # --- DISEÑO ---
        
        # Título Principal
        lbl_titulo = tk.Label(
            self.root, 
            text="Organizador de Archivos 🚀", 
            font=("Segoe UI", 20, "bold"), 
            bg="#1e1e2e", 
            fg="#89b4fa"  # Azul pastel brillante
        )
        lbl_titulo.pack(pady=20)

        # Subtítulo de instrucción
        lbl_instruccion = tk.Label(
            self.root, 
            text="Selecciona la carpeta que deseas organizar:", 
            font=("Segoe UI", 10), 
            bg="#1e1e2e", 
            fg="#a6adc8"
        )
        lbl_instruccion.pack(anchor="w", padx=40)

        # Fila de selección de ruta
        frame_ruta = tk.Frame(self.root, bg="#1e1e2e")
        frame_ruta.pack(fill="x", padx=40, pady=5)

        self.entry_ruta = tk.Entry(
            frame_ruta, 
            textvariable=self.ruta_actual, 
            font=("Segoe UI", 10), 
            bg="#313244", 
            fg="#cdd6f4", 
            insertbackground="#cdd6f4",
            bd=0, 
            highlightthickness=1, 
            highlightbackground="#45475a", 
            highlightcolor="#89b4fa"
        )
        self.entry_ruta.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 10))

        btn_buscar = tk.Button(
            frame_ruta, 
            text="Examinar...", 
            command=self.buscar_carpeta, 
            font=("Segoe UI", 9, "bold"), 
            bg="#45475a", 
            fg="#cdd6f4", 
            activebackground="#585b70", 
            activeforeground="#cdd6f4", 
            bd=0, 
            padx=12, 
            cursor="hand2"
        )
        btn_buscar.pack(side="right")

        # Botón de Acción Principal (Organizar)
        self.btn_organizar = tk.Button(
            self.root, 
            text="ORGANIZAR AHORA", 
            command=self.iniciar_organizacion, 
            font=("Segoe UI", 12, "bold"), 
            bg="#a6e3a1",  # Verde pastel vibrante
            fg="#11111b",  # Texto oscuro contrastante
            activebackground="#94e2d5", 
            activeforeground="#11111b", 
            bd=0, 
            pady=12, 
            cursor="hand2"
        )
        self.btn_organizar.pack(fill="x", padx=40, pady=20)
        
        # Efectos visuales de Hover (pasar el mouse por encima)
        self.btn_organizar.bind("<Enter>", lambda e: self.btn_organizar.configure(bg="#94e2d5"))
        self.btn_organizar.bind("<Leave>", lambda e: self.btn_organizar.configure(bg="#a6e3a1"))

        # Consola de Registro de Actividad
        lbl_consola = tk.Label(
            self.root, 
            text="Historial de organización:", 
            font=("Segoe UI", 10), 
            bg="#1e1e2e", 
            fg="#a6adc8"
        )
        lbl_consola.pack(anchor="w", padx=40)

        # Cuadro de registro estilo consola
        self.txt_log = tk.Text(
            self.root, 
            font=("Consolas", 10), 
            bg="#11111b", 
            fg="#a6e3a1", 
            bd=0, 
            highlightthickness=1, 
            highlightbackground="#45475a"
        )
        self.txt_log.pack(fill="both", expand=True, padx=40, pady=(5, 25))
        
        self.log("Listo para iniciar. Elige una carpeta y presiona 'ORGANIZAR AHORA'.\n")

    def buscar_carpeta(self):
        carpeta = filedialog.askdirectory(initialdir=self.ruta_actual.get())
        if carpeta:
            self.ruta_actual.set(carpeta)

    def log(self, mensaje):
        # Insertar mensaje en la consola de la interfaz
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", mensaje)
        self.txt_log.see("end")  # Hace scroll automático al final
        self.txt_log.configure(state="disabled")

    def iniciar_organizacion(self):
        # Deshabilitar el botón principal durante el proceso
        self.btn_organizar.configure(state="disabled", text="ORGANIZANDO...", bg="#585b70")
        
        # Limpiar la consola de log
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.configure(state="disabled")
        
        # Correr el proceso en un hilo secundario para evitar congelamientos en la ventana
        hilo = threading.Thread(target=self.ejecutar_proceso)
        hilo.start()

    def ejecutar_proceso(self):
        ruta = self.ruta_actual.get()
        organizar_carpeta(ruta, self.log)
        
        # Restaurar el botón en el hilo principal una vez termine
        self.root.after(0, self.restaurar_boton)

    def restaurar_boton(self):
        self.btn_organizar.configure(state="normal", text="ORGANIZAR AHORA", bg="#a6e3a1")

if __name__ == "__main__":
    root = tk.Tk()
    app = OrganizadorGUI(root)
    root.mainloop()
