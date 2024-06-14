import os
import numpy as np
import logging
import sys
import pandas as pd

def dark_spectres(input_directory_dark):

    # Listar archivos de texto en el directorio de entrada
    d_files = os.listdir(input_directory_dark)
    d_text_files = [file for file in d_files if file.endswith('.txt')]

    if not d_text_files:
        logging.warning("No se encontraron archivos de texto en el directorio.")
        return None

    d_all_spectres = []

    # Procesar cada archivo de texto
    for file_name in d_text_files:
        file_path = os.path.join(input_directory_dark, file_name)
        try:
            # Cargar los datos
            calibration, spectre = np.loadtxt(file_path, skiprows=13, unpack=True)
            d_all_spectres.append(spectre)
            logging.info(f"Archivo procesado: {file_name}")
        except Exception as e:
            logging.error(f"Error al cargar {file_name}: {e}")

    # Calcular la media de los espectros
    if d_all_spectres:
        mean_spectres = np.mean(d_all_spectres, axis=0)
        logging.info("Cálculo de la dark correction completado.")
        return mean_spectres
    else:
        logging.warning("No se encontraron espectros.")
        return None


def process_and_merge_spectra(input_directory,
                              header_file_path,
                              num_lines_per_header,
                              date):

    
    logger.info("Procesando archivos de texto en el directorio: %s", input_directory)
    # Listar archivos de texto en el directorio de entrada
    files = os.listdir(input_directory)
    text_files = [file for file in files if file.endswith('.txt')]
    all_spectres = []

    # Procesar cada archivo de texto
    for n,file_name in enumerate(text_files):
        file_path = os.path.join(input_directory, file_name)
        logger.info("Procesando archivo: %s", file_path)
        # Cargar los datos 
        calibration, spectre = np.loadtxt(file_path, skiprows=13, unpack=True)
        spectre = abs(spectre - dark_spectres)

        # Carga los datos de la cabecera (header)
        header_data = np.loadtxt(header_file_path,skiprows=1)

        # Inserta la cabecera 
        spectre = np.insert(spectre, 0, header_data[n])
        tspectre = spectre.reshape(1, -1)
        all_spectres.append(tspectre)
        
        # Añade una columna vacía necesaría para la lectura de los datos
        empty_column = np.full((calibration.shape[0], 1), ' ')
        calibration_with_empty_column = np.column_stack((empty_column, calibration))
        
        
    # Une todos los espectros
    merged_spectre = np.concatenate(all_spectres)
    
    # Reemplaza los valores -1 por una cadena de texto
    merged_spectre = np.where(merged_spectre == -1, date , merged_spectre)

    return calibration_with_empty_column, merged_spectre


# Configuración de logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#Directorios necesarios para las funciones
input_directory_dark = input("Ruta del directorio que contiene los archivos de texto de Dark Correction: ")
if not os.path.isdir(input_directory_dark):
    logger.error("¡Error! La ruta proporcionada no es un directorio válido.")
    sys.exit()
    
input_directory = input("Ruta del directorio que contiene los archivos de texto del espectro: ")
if not os.path.isdir(input_directory):
    logger.error("¡Error! La ruta proporcionada no es un directorio válido.")
    sys.exit()

header_file_path = input("Ruta del archivo de encabezado (header): ")
if not os.path.isfile(header_file_path):
    logger.error("¡Error! La ruta proporcionada no es un archivo válido.")
    sys.exit()

if not header_file_path.lower().endswith('.txt'):
    logger.error("¡Error! El archivo seleccionado no es un archivo de texto (.txt).")
    sys.exit()
    

# Logger para mostrar las opciones de información para num_lines_per_header
info_logger = logging.getLogger("info_logger")    
info_logger.setLevel(logging.INFO)
info_logger.info("Opciones de información para cabecera:")
info_logger.info("1: Solar Zenith Angle")
info_logger.info("2: Azimuth Viewing Angle")
info_logger.info("3: Elevation Viewing Angle")
info_logger.info("4: Date in the DD/MM/YYYY (day/month/ year) format")
info_logger.info("5: Fractional time")
info_logger.info("6: Lambda")

num_lines_per_header = int(input("Cantidad de información introducida (obligado SZA,fecha y Fractional time): "))
if not num_lines_per_header != int:
    logger.error("¡Error! Debe ser un número entero.")
    sys.exit()
    
#Descripcion del archivo
date = input("Ingrese la fecha (dd/mm/yyyy): ")
if not date != str:
    logger.error("¡Error! Debe ser dd/mm/yyyy.")
    sys.exit()

#Llamada a la funcion
dark_spectres = dark_spectres(input_directory_dark)

calibration, merged_spectre = process_and_merge_spectra(input_directory, 
                                                        header_file_path, 
                                                        num_lines_per_header,
                                                        date)


def color_and_highlight(record):
    # Modificar el registro para que aparezca en negrita y en color amarillo
    record.msg = f"\033[1;33m{record.msg}\033[0m"
    return True

# Crear un filtro para el formato deseado
highlight_filter = logging.Filter()
highlight_filter.filter = color_and_highlight
logger.addFilter(highlight_filter)

# Ahora puedes agregar tu mensaje logger.info
logger.info("Tamaño del archivo de calibración: %s",len(calibration))

#Descripcion del archivo
Description = input("Ingrese la descripción del archivo: ")

ruta_salida = input("Ruta del directorio de salida: ")
if not os.path.isdir(ruta_salida):
    logger.error("¡Error! La ruta proporcionada no es un directorio válido.")
    sys.exit()

#Salidas del archivo
output_clb = os.path.join(ruta_salida, f"calibration_{Description}.clb")
output_spe = os.path.join(ruta_salida, f"merged_spectre_{Description}.SPE")

#Guardar los datos
np.savetxt(output_clb,calibration, fmt="%s")
np.savetxt(output_spe, merged_spectre,fmt="%s")
