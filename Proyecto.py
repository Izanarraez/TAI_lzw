# -*- coding: utf-8 -*-
"""
Created on Sun Oct 19 19:55:09 2025

@author: Izan, Daniel Y Victor

Herramienta de compresión y descompresión LZW.

Este script permite:
    - Codificar archivos de texto (.txt) usando el algoritmo LZW.
    - Descomprimir archivos previamente comprimidos.
    - Comparar dos archivos de texto para comprobar si son idénticos.
"""

import pickle
import difflib
from bitarray import bitarray
from bitarray.util import int2ba
from bitarray.util import ba2int

TAMANIOBITSCODIFICACION = 12

#Clase principal de la ejecucion 
def main():
    """
    Menú principal del programa.

    Permite al usuario seleccionar entre:
        1. Codificar un archivo de texto usando LZW.
        2. Descomprimir un archivo previamente comprimido.
        3. Comparar dos archivos .txt línea por línea.
        4. Salir del programa.
    """
    
    salida = True
    
    while salida:
        print("---MENÚ PRINCIPAL---\n")
        print("Pulsa 1 si quieres codificar un texto");
        print("Pulsa 2 si quieres decodificar un texto");
        print("Pulsa 3  para comparar dos txt")
        print("Pulsa 4  para salir\n")
        
        respuesta = input("Selecciona una opcion: ")
        
        if respuesta == "1":
            codificacion()
            
        if respuesta == "2":
            decodificacion()
           
        if respuesta == "3":
            comparar_detallado()

        if respuesta == "4":
            print("Saliendo del programa")
            salida = False
            
        else:
            print("\nOpción incorrecta\n\n")
            
            

def codificacion():
    """
    Ejecuta el proceso de codificación LZW.

    Solicita al usuario el nombre de un archivo .txt, genera la lista de 
    códigos LZW mediante 'comprime_a_clave()', y posteriormente llama a 
    la función encargada de empaquetar y guardar los datos comprimidos.
    """
    
    nombreArchivo = input("Introduce el nombre del archivo (sin .txt) que quieres codificar en lzw: ").strip()
    if nombreArchivo.endswith(".txt"):
        nombreArchivo = nombreArchivo[:-4] #Elimina la extensión si el usuario la introdujo
     
    listaCodigos = comprime_a_clave(nombreArchivo)
    if not listaCodigos:
        print("No se generaron códigos (archivo vacío o no encontrado).")
        return
     
    #funcion comprimir



def decodificacion():
    """
    Ejecuta el proceso de descompresión LZW.
    
    Solicita al usuario el archivo comprimido (.lzw) y el nombre del archivo 
    de salida. Llama a 'cargar_y_lzw_descompresion()' para reconstruir el 
    contenido original y guardarlo en un archivo .txt.
    """
    
    nombreArchivo = input("Introduce el nombre del archivo comprimido (sin .lzw): ").strip()

    if nombreArchivo.endswith(".lzw"):
        nombreArchivo = nombreArchivo[:-4]
    
    nombreSalida = input("Introduce el nombre del archivo de salida (sin .txt): ").strip()
    if nombreSalida == "": # Si no escribe nada, se pone un nombre automático
        nombreSalida = nombreArchivo.replace(".lzw", "_descomprimido.txt")
    else:
        if nombreSalida.endswith(".txt"):
            nombreSalida = nombreSalida[:-4]
    
    # Ejecutar descompresión
    texto = cargar_y_lzw_descompresion(nombreArchivo, nombreSalida)
    
    if texto is None:
        print("No se pudo descomprimir el archivo.")
    else:
        print("Archivo descomprimido correctamente en: {nombreSalida}")
    
    
    
def cargar_y_lzw_descompresion(archivo_comprimido, archivo_salida):
    """
    Carga un archivo comprimido mediante pickle y realiza la descompresión LZW.
 
    Parámetros
    ----------
    archivo_comprimido : str
        Nombre del archivo .lzw que contiene los códigos comprimidos.
    archivo_salida : str
        Ruta del archivo .txt donde se guardará el texto descomprimido.
 
    Retorna
    -------
    str or None
        El texto descomprimido, o None si ocurre un error.
    """
   
    try:
        with open(archivo_comprimido, 'rb') as archivo:
            datos = pickle.load(archivo)
        
        bits = bitarray()
        bits.extend(datos['bits'])

        longitud_codigo = datos['longitud_codigo']    
        
        codigos = bits_a_codigos(bits, longitud_codigo)
        
        texto_descomprimido = lzw_descompresion(codigos)

        if archivo_salida:
            with open(archivo_salida, 'w', encoding='utf-8') as archivo:
                archivo.write(texto_descomprimido)
            print(f"\nArchivo descomprimido guardado: {archivo_salida}")
        
        return texto_descomprimido
        
    except Exception as e:
        print(f"Error al cargar/descomprimir: {e}")
        return None


def bits_a_codigos(bits, longitud_codigo):
    """
    Convierte un bitarray en una lista de códigos LZW de longitud fija.

    Parámetros
    ----------
    bits : bitarray
        Secuencia de bits que contiene los códigos LZW compactados.
    longitud_codigo : int
        Tamaño en bits de cada código.

    Retorna
    -------
    list[int]
        Lista de códigos LZW interpretados desde el bitarray.
    """

    codigos = []
    cadena_bits = bits.to01()

    for i in range(0, len(cadena_bits), longitud_codigo):
        chunk = cadena_bits[i:i+longitud_codigo]
        if len(chunk) == longitud_codigo:
            codigos.append(int(chunk, 2))

    return codigos


def lzw_descompresion(codigos):
    """
    Descompresión del algoritmo LZW.

    Reconstruye el texto original a partir de la lista de códigos numéricos,
    utilizando la tabla dinámica del diccionario LZW.

    Parámetros
    ----------
    codigos : list[int]
        Códigos generados previamente durante la compresión.

    Retorna
    -------
    str
        Texto original reconstruido a partir de los códigos LZW.
    """

    diccionario = {i: chr(i) for i in range(256)}
    proximo_codigo = 256

    if not codigos:
        return ""
    
    codigo_anterior = codigos[0]
    resultado = diccionario[codigo_anterior]
    cadena_anterior = resultado
    
    for codigo_actual in codigos[1:]:
        if codigo_actual in diccionario:
            entrada_actual = diccionario[codigo_actual]
        else:
            entrada_actual = cadena_anterior + cadena_anterior[0]
        
        resultado += entrada_actual
        
        diccionario[proximo_codigo] = cadena_anterior + entrada_actual[0]
        proximo_codigo += 1
        
        cadena_anterior = entrada_actual
    
    return resultado


#metodo para convertir una letra a clave del diccionario
def comprime_a_clave():
    """
    Comprime el contenido de un archivo de texto usando el algoritmo LZW.

    Solicita al usuario el nombre del archivo .txt a procesar y recorre su 
    contenido carácter por carácter, generando la lista de códigos LZW 
    correspondiente.

    Retorna
    -------
    list[int]
        Lista de códigos generados durante el proceso de compresión.
    """

    
    dicc = { x: chr(x) for x in range(256)}
    dicc_inverso = { chr(x) : x for x in range(256)} #poner valor en listaCodigos
    
    cadenaActual = ""
    cadenaSecundaria = ""
    
    listaCodigos = []
    
    tamanio = 256
    
    nombreArchivo = input("introduce el nombre del archivo que quieres codificar en lzw")
    
    with open(nombreArchivo+".txt",'r',encoding="utf-8") as archivo:
    
        for fila in archivo:
        
            for caracter in fila:
            
                cadenaActual = cadenaSecundaria + caracter
                
                if cadenaActual in dicc_inverso:
                    
                    cadenaSecundaria = cadenaActual
                    
                else:
                    
                    listaCodigos.append(dicc_inverso[cadenaSecundaria])
                    
                    if tamanio < 2**TAMANIOBITSCODIFICACION: #12 bits
                        dicc[tamanio] = cadenaActual
                        dicc_inverso[cadenaActual] = tamanio
                        tamanio = tamanio + 1
                    
                    cadenaSecundaria = caracter
    
        if cadenaSecundaria:
            listaCodigos.append(dicc_inverso[cadenaSecundaria])
    
    dicc.clear()
    dicc_inverso.clear()
    
    return listaCodigos

#Comparador de tos documentos para ver si son iguales
def comparar_detallado():
    """
    Compara dos archivos de texto línea por línea e informa si son idénticos.

    Si existen diferencias, genera un diff estilo 'unified diff' para mostrar 
    con detalle las líneas modificadas.

    Solicita ambos nombres de archivo al usuario.
    """


    f1_nombre = input("Archivo original: ") + ".txt"
    f2_nombre = input("Archivo decodificado: ") + ".txt"

    try:
        # Usamos readlines() para comparar línea por línea
        with open(f1_nombre, 'r', encoding='utf-8') as f1, \
             open(f2_nombre, 'r', encoding='utf-8') as f2:
            
            texto1 = f1.readlines()
            texto2 = f2.readlines()

            if texto1 == texto2:
                print("\nLos archivos son idénticos.")
            else:
                print("\nSe encontraron diferencias:")
                
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