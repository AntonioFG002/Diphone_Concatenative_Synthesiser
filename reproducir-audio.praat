# Descripción: Reproduce un archivo de audio pasado como parámetro.
# Uso: Se ejecuta desde línea de comandos con el nombre del archivo como argumento.

form Reproducir audio
    text nombre_audio "Nombre del archivo de audio"
endform

# Leer el archivo de audio
Read from file... 'nombre_audio$'

# Reproducir el archivo
Play

# Finalizar el script
exit
