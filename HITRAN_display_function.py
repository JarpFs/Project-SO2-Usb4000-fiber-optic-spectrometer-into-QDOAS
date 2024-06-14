# -*- coding: utf-8 -*-

import numpy as np
import logging
import os
import sys

# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def procesar_archivo(nombre_archivo, inicio_espectro, fin_espectro):
    with open(nombre_archivo, 'r') as file:
        # Leer la primera línea y descartarla
        file.readline()
        
        array_datos = []
        for line in file:
            # Divide cada línea en elementos individuales y conviértelos a números si es necesario
            elementos = [float(x) for x in line.split()]
            array_datos.extend(elementos)
            
    cantidad_puntos=len(array_datos)
    # Wavenumbers para cada dato
    espectro = np.arange(
        inicio_espectro, 
        fin_espectro + (fin_espectro - inicio_espectro) / (cantidad_puntos - 1), 
        (fin_espectro - inicio_espectro) / (cantidad_puntos - 1)
        )

    salida = np.zeros((len(array_datos), 2))

    salida[:, 0] = (1/espectro) * 10**(7)
    salida[:, 1] = array_datos

    return salida

def solicitar_valor(mensaje):
    while True:
        valor = input(mensaje)
        try:
            valor = float(valor)
            if valor >0 :
                return valor
            else:
                logger.error("El valor ingresado debe ser mayor que cero. Por favor, ingrese un número válido.")
        except ValueError:
            logger.error("El valor ingresado no es válido. Por favor, ingrese un número válido.")

# Solicitar los valores al usuario
while True:
    nombre_archivo = input("Ingrese la ruta del archivo con .xsc o .txt: ")
    if os.path.isfile(nombre_archivo) and nombre_archivo.lower().endswith(('.xsc', '.txt')):
        break
    else:
        logger.error("El archivo especificado no existe o no tiene una extensión válida (.xsc o .txt). Inténtelo de nuevo.")

#Valores de HITRAN
inicio_espectro = solicitar_valor("Ingrese el valor de inicio del espectro (range/cm^{-1}): ")
fin_espectro = solicitar_valor("Ingrese el valor final del espectro (range/cm^{-1}): ")

#Nombres del archivo
Molecula = input("Ingrese el nombre de la molecula del archivo: ")
Description = input("Ingrese la descripción del archivo: ")

#Directorio de salida
ruta_salida = input("Ingrese la ruta de salida del archivo: ")
if not os.path.isdir(ruta_salida):
    logger.error("¡Error! La ruta proporcionada no es un directorio válido.")
    sys.exit()
    
output_file = os.path.join(ruta_salida, f"{Molecula}_{Description}.xs")

# Verificar el formato del espectro
if inicio_espectro >= fin_espectro:
    logger.error("¡Error! Por favor, asegúrese de que el valor de inicio del espectro sea menor que el valor final.")
else:
    resultado = procesar_archivo(nombre_archivo, inicio_espectro, fin_espectro)
    logger.info("¡Procesamiento completado con éxito!")
    np.savetxt(output_file,resultado,delimiter='  ',
            header="X=wavelenghts nm Y=Cross section cm^{2]/molecule")
