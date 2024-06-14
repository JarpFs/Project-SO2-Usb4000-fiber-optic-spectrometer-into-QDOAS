import numpy as np
import pylab as py
import pandas as pd
import os
import logging
import sys


# Configuración del logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#Borra las gráficas 
py.clf()

#prueba = pd.read_table("W:\Programas\QDOAS_Windows_3.5.0\TEST1\Output\Prueba_4.txt", skiprows=1)

# Obtener la ruta del archivo del usuario
ruta_archivo = input("Por favor, ingrese la ruta del archivo: ")
if not os.path.isfile(ruta_archivo):
    logger.error("¡Error! La ruta proporcionada no es un archivo válido.")
    sys.exit()
    
# Logger para mostrar las opciones de información para num_lines_per_header
info_logger = logging.getLogger("info_logger")    
info_logger.setLevel(logging.INFO)


# Leer el archivo con pandas
data = pd.read_table(ruta_archivo, skiprows=1)

print(
      'Asegurese de que aparezcan los nombres de las columnas correctamente(Ej:NO2.SlCol(o3))'
      ,data.keys()
      )

print("\n")

info_logger.info("Analysis Windows")

Analysis = input("Ingrese el nombre del Analysis Windows: ")
Molecula = input("Ingrese la molecula que estudia: ")
info_logger.info("Opciones del archivo para gráfica:")
info_logger.info("Fractional time,SZA,Azim. viewing angle,Elev. viewing angle")

Plot=input("Ingrese el eje interesado en el estudio sin las comillas: ")

Convertir = input("¿Quieres ver la VCD? (y/n): ")

#Proceso estadistico para eliminar los valores más alejados
def procesar_datos(data,Analysis,Molecula):
    # Encontrar el índice del valor máximo que proviene del espectro que es de referencia para el resto
    indice_maximo = data[f"{Analysis}.SlCol({Molecula})"].idxmax()
    
    # Eliminar la fila correspondiente al índice máximo
    data_proceso = data.drop(index=indice_maximo)
    
    # Aplicar valor absoluto y sumar 1 a los datos de la columna 'Columna_A'
    data_proceso[f"{Analysis}.SlCol({Molecula})"] = data_proceso[f"{Analysis}.SlCol({Molecula})"].abs() + 1
    
    # Calcular la media y la desviación estándar de la columna 'Columna_A'
    media = data_proceso[f"{Analysis}.SlCol({Molecula})"].mean()
    desviacion_estandar = data_proceso[f"{Analysis}.SlCol({Molecula})"].std()
    
    # Definir los límites inferior y superior basados en la media y la desviación estándar
    umbral_inferior = media - 2 * desviacion_estandar
    umbral_superior = media + 2 * desviacion_estandar
    
    # Filtrar las filas que contienen valores atípicos
    data_proceso = data_proceso[(data_proceso[f"{Analysis}.SlCol({Molecula})"]>= umbral_inferior) 
                     & (data_proceso[f"{Analysis}.SlCol({Molecula})"] <= umbral_superior)]
    
    return data_proceso

def SCR_or_VCD(convertir,unidades,data):
    
    scd = data[f"{Analysis}.SlCol({Molecula})"]
    sza = data['SZA']
    
    if f"{Analysis}.SlErr({Molecula})" in data.columns: 
        scd_error = data[f"{Analysis}.SlErr({Molecula})"]
    else:
        scd_error = 0
    
    #Condiciones para  transformar la SCD a VCD
    if convertir=='Y' or convertir=='y':
        
        sza = sza * (np.pi / 180)
        #Calcular la aproximación del AMF
        amf=1/np.cos(sza)
        
        vcd = scd/amf
     
        vcd_error =  scd_error/amf
        
        #Convertir de mol/cm2 a DU
        if unidades=="Y" or unidades=='y':
            vcd = vcd/2.69E16
            vcd_error = vcd_error/2.69E16
            
    else:#Devuelve la SCD
        vcd = scd
        vcd_error = scd_error
        
    return vcd,vcd_error
  
#Graficacion de las moleculas con su respectivo error  
def grafica_and_errores(Molecula,Plot,vcd,vcd_erro,data):
    
    x_axis = data[f'{Plot}']
    p1 = py.plot(x_axis,vcd,"r.")
    
    if f"{Analysis}.SlErr({Molecula})" in data.columns:
        
        p_error = py.errorbar(x_axis, 
                    vcd, 
                    yerr=abs(vcd_error),
                    fmt='s',
                    markersize=0,
                    capsize=5, 
                    ecolor="y")       
    else:
        p_error=logger.warning("No tiene columna de error")
              
    return p1,p_error

#Unidades del plot que cambian según los parametros elegidos
def unidad_plot_y(convertir):
    unidades = 'n'
    unidad_y = '$molec \cdot cm^{-2}$'
    if convertir == 'Y' or convertir == 'y':
        unidades = input("¿Unidades en DU? (y/n): ")
        
        if unidades== 'Y' or unidades == 'y':
            unidad_y = 'DU'
            
    else:
        unidad_y = '$molec \cdot cm^{-2}$'
    return unidades,unidad_y


#Unidades del plot que cambian según los parametros elegidos
def unidad_plot_x(unidad):
    if unidad=='SZA' or unidad=='Azim. viewing angle' or unidad=='Elev. viewing angle':
        magnitud="Grado sexagesimal"
        
    if unidad=='Fractional time':
        magnitud="Horas"
           
    return magnitud

#Llamada a las funciones
data_proceso = procesar_datos(data,
                              Analysis,
                              Molecula)

Unidades,Unidad_y=unidad_plot_y(Convertir)

Unidad_x = unidad_plot_x(Plot)

vcd,vcd_error = SCR_or_VCD(Convertir,
                           Unidades,
                           data_proceso)

grafica_and_errores(Molecula,
                    Plot,vcd,
                    vcd_error,
                    data_proceso)


Titulo=input("Ingrese el título del plot: ")
#Graficamos lo que queremos ver
py.xlabel(f'{Plot} {Unidad_x}')
py.ylabel(f'{Molecula} {Unidad_y}')
py.title(f"{Titulo}")
py.grid()
py.show()
