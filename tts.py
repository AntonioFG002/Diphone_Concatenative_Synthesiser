import sys
import re
from pydub import AudioSegment
#from pydub.playback import play
import os
import subprocess

# Directorio donde están almacenados los archivos de los difonos
DIFONOS_DIR = "difonos"

# Función que verifica las restricciones de la palabra
def validar_palabra(palabra):

    if " " in palabra:
        raise ValueError("Error: La palabra no puede contener espacios.")
    
    if not re.match(r"^[abflmtsA?]*$", palabra):
        raise ValueError("Error: La palabra contiene caracteres no permitidos.")
    
    if palabra[0].lower() == 'm':
        raise ValueError("Error: La palabra no puede empezar con 'm'.")
    
    if "sm" in palabra.lower():  
        raise ValueError("Error: La palabra no puede contener la secuencia 'sm'.")
    
    if "?" in palabra:
        if palabra.count('?') > 1:
            raise ValueError("La palabra solo puede contener un '?' y debe estar al final.")
        if palabra[-1] != '?':
            raise ValueError("El '?' debe estar al final de la palabra.")
        if len(palabra) > 31:
            raise ValueError("La palabra no puede tener más de 31 caracteres si contiene un '?'.")
    else:
        if len(palabra) > 30:
            raise ValueError("La palabra no puede tener más de 30 caracteres si no contiene un '?'.")
        
    return True

def generar_secuencia_difonos(palabra):
    difonos = []

    if palabra.endswith('?'):
        palabra = palabra[:-1]

    difonos.append(f"[_{palabra[0]}]") 

    for i in range(len(palabra) - 1):
        difonos.append(f"[{palabra[i]}{palabra[i+1]}]")  

    difonos.append(f"[{palabra[-1]}_]")  

    return difonos


def cargar_difono(difono, entonacion):
    if(entonacion):
        difono_path = os.path.join(DIFONOS_DIR, f"TMP_{difono}.wav")
    else:
        difono_path = os.path.join(DIFONOS_DIR, f"Df_{difono}.wav")

    if os.path.isfile(difono_path):
        return AudioSegment.from_wav(difono_path)
    else:
        print(f"Advertencia: No se encontró el archivo para el difono '{difono}' en {difono_path}.")
        return None
    
def contiene_a_mayuscula(difono):
    return 'A' in difono

def sintetizar(secuencia, output_path):
    
    output_audio = AudioSegment.silent(duration=0)

    for difono in secuencia:
        entonacion = contiene_a_mayuscula(difono)
        difono_audio = cargar_difono(difono,entonacion)
        if difono_audio:
            output_audio += difono_audio
        else:
            print(f"Advertencia: El difono '{difono}' no tiene un archivo .wav correspondiente en '{DIFONOS_DIR}'.")

    output_audio = output_audio.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    output_audio.export(output_path, format="wav")

# Función para ejecutar comandos con manejo de errores
def ejecutar_comando(comando):
    
    try:
        subprocess.run(comando, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {' '.join(comando)}")
        print(f"Detalles del error: {e}")
        sys.exit(1)

def reproducir_audio_praat(audio_path, praat_script_path):
    
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"El archivo de audio '{audio_path}' no existe.")
    if not os.path.isfile(praat_script_path):
        raise FileNotFoundError(f"El script de Praat '{praat_script_path}' no existe.")
    
    comando = [PRAAT_DIR + "\\praat.exe", praat_script_path, audio_path]
    try:
        subprocess.run(comando, check=True)
        print(f"Reproducción completada para: {audio_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el script de Praat: {e}")

# Prosodia de preguntas
PRAAT_DIR = "D:\\Descargas\\praat6421_win-intel64"

# Obtener la ubicación del script tts.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def extraer_pitch_track(audio_path, pitch_tier_path, min_pitch=50, max_pitch=300):
    
    script_path = os.path.join(SCRIPT_DIR, "extraer-pitch-track.praat")
    if not os.path.isfile(script_path):
        raise FileNotFoundError(f"El script {script_path} no fue encontrado.")
    
    comando = [
        os.path.join(PRAAT_DIR, "praat.exe"), script_path,
        audio_path, pitch_tier_path, str(min_pitch), str(max_pitch)
    ]
    ejecutar_comando(comando)
    return pitch_tier_path
    

def modificar_pitch_tier(pitch_tier_path, pitch_tier_mod_path, factor=1.2):
   
    if not os.path.isfile(pitch_tier_path):
        raise FileNotFoundError(f"El archivo {pitch_tier_path} no existe.")
    
    with open(pitch_tier_path, "r") as f:
        lines = f.readlines()
    
    with open(pitch_tier_mod_path, "w") as f:
        for line in lines:
            if line.strip().startswith("value ="):
                valor_actual = float(line.split("=")[-1].strip())
                nuevo_valor = valor_actual * factor  # Ajusta el pitch
                f.write(f"value = {nuevo_valor}\n")
            else:
                f.write(line)

def resintetizar_audio(audio_path, pitch_tier_path, output_path, min_pitch=50, max_pitch=300):
    
    script_path = os.path.join(SCRIPT_DIR, "reemplazar-pitch-track.praat")
    if not os.path.isfile(script_path):
        raise FileNotFoundError(f"El script {script_path} no fue encontrado.")

    pitch_tier_path = os.path.abspath(pitch_tier_path)
    output_path = os.path.abspath(output_path)

    comando = [
        os.path.join(PRAAT_DIR, "praat.exe"), script_path,
        audio_path, pitch_tier_path, output_path, str(min_pitch), str(max_pitch)
    ]
    ejecutar_comando(comando)
    




def modificar_pitch_ultimo_40(audio_path, pitch_tier_path, pitch_tier_mod_path, min_pitch=50, max_pitch=300, factor=1.2):
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(f"El archivo {audio_path} no existe.")

    audio = AudioSegment.from_wav(audio_path)
    duracion_total = len(audio)
    duracion_ultimo_40 = int(duracion_total * 0.4)
    

    inicio_80 = audio[:duracion_total - duracion_ultimo_40]
    ultimo_40 = audio[duracion_total - duracion_ultimo_40:]
    
    temp_last_40_path = "temp_last_40.wav"
    ultimo_40.export(temp_last_40_path, format="wav")
    
    pitch_tier_path = extraer_pitch_track(temp_last_40_path, pitch_tier_path, min_pitch, max_pitch)
    

    modificar_pitch_tier(pitch_tier_path, pitch_tier_mod_path, factor=factor)
   
    temp_last_40_mod_path = "temp_last_40_mod.wav"
    resintetizar_audio(temp_last_40_path, pitch_tier_mod_path, temp_last_40_mod_path, min_pitch, max_pitch)
    
    ultimo_40_modificado = AudioSegment.from_wav(temp_last_40_mod_path)
    
    audio_modificado = inicio_80 + ultimo_40_modificado
    
    audio_modificado.export(audio_path, format="wav")
    print("Archivo de salida esperado:", audio_path)
    
    os.remove(temp_last_40_path)
    os.remove(temp_last_40_mod_path)
    os.remove(pitch_tier_path)
    os.remove(pitch_tier_mod_path)
#Main

if __name__ == "__main__":
   
    if len(sys.argv) != 3:
        print("La palabra no puede tener espacios, o el número de parámetros es incorrecto. Uso: python tts.py palabra output_wav")
        sys.exit(1)

    palabra = sys.argv[1]
    palabra_sin_modificar = palabra

    if not validar_palabra(palabra):
        sys.exit(1)  # Salir si no cumple las restricciones

    output_wav = sys.argv[2]

    reproducir_audio = input("¿Quieres reproducir el audio automáticamente? (si/no): ").lower() in ['si', 's', 'y', 'yes']

    secuencia_difonos = generar_secuencia_difonos(palabra)
    print(f"Secuencia de difonos generada: {secuencia_difonos}")

    sintetizar(secuencia_difonos, output_wav)

    if palabra_sin_modificar[-1] == '?':
       
        factor_prosodia = 1.2 
        min_pitch, max_pitch = 75, 500

        pitch_tier_path = "temp.PitchTier"
        pitch_tier_mod_path = "temp-mod.PitchTier"
        
        if reproducir_audio != False:
            praat_script_path = "reproducir-audio.praat"
            modificar_pitch_ultimo_40(output_wav, pitch_tier_path, pitch_tier_mod_path, factor=1.2)
            reproducir_audio_praat(output_wav, praat_script_path)
        else:
            modificar_pitch_ultimo_40(output_wav, pitch_tier_path, pitch_tier_mod_path, factor=1.2)


#C:\Users\awela\Documents\GitHub\Sintetizador--concatenativo-de-difonos-\pruebas\taflamalatablamama.wav
    elif reproducir_audio != False:
        praat_script_path = "reproducir-audio.praat"
        #audio_path = "pruebas\\" + palabra_sin_modificar + ".wav"
        reproducir_audio_praat(output_wav, praat_script_path)    