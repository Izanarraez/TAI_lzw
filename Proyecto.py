# -*- coding: utf-8 -*-
"""
Created on Sun Oct 19 19:55:09 2025

@author: izana
"""
from bitarray import bitarray
from bitarray.util import int2ba
from bitarray.util import ba2int
import difflib


tamañoBitsCodificacion = 12


#Clase principal de la ejecucion 
def main():
    
    salida = True
    
    while salida:
        print("Pulsa 1 si quieres codificar un texto");
        print("Pulsa 2 si quieres decodificar un texto");
        print("Pulsa 3  para salir")
        print("Pulsa 4  para comparar dos txt")
        
        respuesta = input("Selecciona una opcion:")
        
        if respuesta == "1": #Codificar
            codificacion()
            
        if respuesta == "2": #Decodificar
            decodificacion()
           
        if respuesta == "3":
            print("Saliendo del programa")
            salida = False
            
        if respuesta == "4":
            comparar_detallado()


#metodo para convertir una letra a clave del diccionario
def comprime_a_clave():
    
    dicc = { x: chr(x) for x in range(256)}
    dicc_inverso = { chr(x) : x for x in range(256)} #poner valor en listaCodigos
    
    cadenaActual = ""
    cadenaSecundaria = ""
    
    listaCodigos = []
    
    tamaño = 256
    
    nombreArchivo = input("introduce el nombre del archivo que quieres codificar en lzw")
    
    with open(nombreArchivo+".txt",'r',encoding="utf-8") as archivo:
    
        for fila in archivo:
        
            for caracter in fila:
            
                cadenaActual = cadenaSecundaria + caracter
                
                if cadenaActual in dicc_inverso:
                    
                    cadenaSecundaria = cadenaActual
                    
                else:
                    
                    listaCodigos.append(dicc_inverso[cadenaSecundaria])
                    
                    if tamaño < 2**tamañoBitsCodificacion: #12 bits
                        dicc[tamaño] = cadenaActual
                        dicc_inverso[cadenaActual] = tamaño
                        tamaño = tamaño + 1
                    
                    cadenaSecundaria = caracter
    
        if cadenaSecundaria:
            listaCodigos.append(dicc_inverso[cadenaSecundaria])
    
    dicc.clear()
    dicc_inverso.clear()
    
    return listaCodigos

#Comparador de tos documentos para ver si son iguales
def comparar_detallado():
    f1_nombre = input("Archivo original: ") + ".txt"
    f2_nombre = input("Archivo decodificado: ") + ".txt"

    try:
        # Usamos readlines() para comparar línea por línea
        with open(f1_nombre, 'r', encoding='utf-8') as f1, \
             open(f2_nombre, 'r', encoding='utf-8') as f2:
            
            texto1 = f1.readlines()
            texto2 = f2.readlines()

            if texto1 == texto2:
                print("\n✅ Los archivos son idénticos.")
            else:
                print("\n❌ Se encontraron diferencias:")
                
                # Generamos un reporte de diferencias
                diff = difflib.unified_diff(
                    texto1, texto2, 
                    fromfile=f1_nombre, 
                    tofile=f2_nombre, 
                    lineterm=''
                )
                
                for linea in diff:
                    print(linea)
                    
    except FileNotFoundError:
        print("No se encontró alguno de los archivos.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()