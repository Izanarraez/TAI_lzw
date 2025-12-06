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

import os
from bitarray import bitarray
from bitarray.util import int2ba
from bitarray.util import ba2int

MAXIMO_BITS_CODIFICACION = 12
MAXIMO_NUMERO_BITS = 2**MAXIMO_BITS_CODIFICACION
    
   
def codificacion():
    
    """
    Ejecuta el proceso completo de compresión LZW:

    - Solicita al usuario un archivo .txt.
    - Llama a 'comprime_a_clave' para obtener los códigos LZW.
    - Convierte los códigos en bits.
    - Guarda el archivo resultante .lzw.

    Retorna:
        None
    """
     
    resultado = comprime_a_clave()
    
    if not resultado:
        print("No se generaron los códigos o hubo un error.")
        return

    listaCodigos, nombreArchivoBase = resultado
    
    try:
        bits = bitarray()
        # Convertimos cada código (int) a su representación en 12 bits
        for codigo in listaCodigos:
            bits.extend(int2ba(codigo, length=MAXIMO_BITS_CODIFICACION))
        
        nombreSalida = nombreArchivoBase + ".lzw"
        
        with open(nombreSalida, 'wb') as archivo:
            bits.tofile(archivo)
            
        print(f"\nArchivo comprimido guardado exitosamente: {nombreSalida}")
        
    except Exception as e:
        print(f"Error al guardar el archivo comprimido: {e}")
     

def decodificacion():
    """
    Ejecuta el proceso de descompresión LZW.
    
    - Solicita al usuario un archivo .lzw.
    - Convierte los bits a códigos.
    - Descomprime mediante LZW.
    - Guarda el archivo .txt resultante.

    Retorna:
        None
    """
    
    nombreArchivo = input("Introduce el nombre del archivo comprimido (sin .lzw): ").strip()

    if nombreArchivo.endswith(".lzw"):
        nombreSinExtension = nombreArchivo[:-4]
    nombreArchivo += ".lzw"
        
    nombreSalida = input("Introduce el nombre del archivo de salida (sin .txt): ").strip()
    
    if nombreSalida == "": # Si no escribe nada, se pone un nombre automático
        nombreSalida = nombreSinExtension + "_descomprimido.txt"
    else:
        if nombreSalida.endswith(".txt"):
            nombreSalida = nombreSalida[:-4]
        nombreSalida += ".txt"
    
    textoBytes = cargar_y_lzw_descompresion(nombreArchivo, nombreSalida)
    
    if textoBytes is None:
        print("No se pudo descomprimir el archivo.")
        
        
def comparar_detallado():
    """
    Compara dos archivos byte a byte.

     Solicita:
        - Nombre del archivo original (sin .txt).
        - Nombre del archivo descomprimido (sin .txt).

    Retorna:
        None
    """

    f1_nombre = input("Archivo original (sin .txt): ") + ".txt"
    f2_nombre = input("Archivo decodificado (sin .txt): ") + ".txt"

    if not os.path.exists(f1_nombre) or not os.path.exists(f2_nombre):
        print("No se encontró alguno de los archivos.")
        return

    try:
        # Usamos modo 'rb' para comparación exacta byte a byte
        with open(f1_nombre, 'rb') as f1, open(f2_nombre, 'rb') as f2:
            contenido1 = f1.read()
            contenido2 = f2.read()

            if contenido1 == contenido2:
                print("\n¡ÉXITO! Los archivos son IDÉNTICOS byte a byte.")
            else:
                print("\nLos archivos son DIFERENTES.")
                print(f"Tamaño original: {len(contenido1)} bytes")
                print(f"Tamaño nuevo:    {len(contenido2)} bytes")
                
                # Muestra donde se encuentra el primer fallo
                for i, (b1, b2) in enumerate(zip(contenido1, contenido2)):
                    if b1 != b2:
                        print(f"Primera diferencia en el byte {i}: Original={b1}, Nuevo={b2}")
                        return
                    
    except Exception as e:
        print(f"Ocurrió un error: {e}")



def cargar_y_lzw_descompresion(archivo_comprimido, archivo_salida):
    """
    Carga un archivo comprimido mediante pickle y realiza la descompresión LZW.
 
    Parámetros:
        archivo_comprimido (str): ruta al archivo .lzw.
        archivo_salida (str): nombre del archivo .txt resultante.

    Retorna:
        bytes: contenido descomprimido.
        None: si ocurre un error.
    """
    if not os.path.exists(archivo_comprimido):
       print(f"Error: El archivo {archivo_comprimido} no existe.")
       return None
    
    try:
        bits = bitarray()
        with open(archivo_comprimido, 'rb') as archivo:
            bits.fromfile(archivo)  
        
        codigos = bits_a_codigos(bits, MAXIMO_BITS_CODIFICACION)
        texto_descomprimido = lzw_descompresion(codigos)

        if archivo_salida:
            with open(archivo_salida, 'wb') as archivo:
                archivo.write(texto_descomprimido)
            print(f"\nArchivo descomprimido guardado: {archivo_salida}")
            
        return texto_descomprimido
        
        
    except Exception as e:
        print(f"Error al cargar/descomprimir: {e}")
        return None


def bits_a_codigos(bits, longitud_codigo):
    """
    Convierte un bitarray en una lista de códigos LZW.

    Parámetros:
        bits (bitarray): secuencia de bits.
        longitud_codigo (int): longitud fija de cada código LZW.

    Retorna:
        list[int]: lista de enteros que representan códigos LZW.
    """

    codigos = []

    for i in range(0, len(bits), longitud_codigo):
        chunk = bits[i:i+longitud_codigo]
        if len(chunk) == longitud_codigo:
            codigos.append(ba2int(chunk))

    return codigos
   

def lzw_descompresion(codigos):
    """
    Descomprime una lista de códigos mediante el algoritmo LZW.

    Parámetros:
        codigos (list[int]): lista de códigos LZW.

    Retorna:
        bytes: texto reconstruido.
    """

    diccionario = {i: bytes([i]) for i in range(256)}
    proximo_codigo = 256

    if not codigos:
        return b""
    
    resultado = bytearray()
    codigo_anterior = codigos[0]
    cadena_anterior = diccionario[codigo_anterior]
    resultado.extend(cadena_anterior)
    
    for codigo_actual in codigos[1:]:
        if codigo_actual in diccionario:
            entrada_actual = diccionario[codigo_actual]
        elif codigo_actual == proximo_codigo:
            entrada_actual = cadena_anterior + bytes([cadena_anterior[0]]) 
        else:
            raise ValueError(f"Código incorrecto en descompresión: {codigo_actual}")
        
        resultado.extend(entrada_actual)
        
        # Solo añadimos al diccionario si cabe dentro del límite de bits
        if proximo_codigo < MAXIMO_NUMERO_BITS:
            diccionario[proximo_codigo] = cadena_anterior + bytes([entrada_actual[0]])
            proximo_codigo += 1
        
        cadena_anterior = entrada_actual
    
    return bytes(resultado)


def comprime_a_clave():
    """
    Comprime el contenido de un archivo .txt usando LZW.

    Solicita el nombre del archivo al usuario.

    Retorna:
        tuple: (listaCodigos, nombreArchivo)
        None: si ocurre un error.
    """

    dicc_inverso = { bytes([x]) : x for x in range(256)} #pone valor en listaCodigos
    cadenaActual = b""
    cadenaSecundaria = b""
    listaCodigos = []
    tamanio = 256
    
    nombreArchivo = input("Introduce el nombre del archivo(sin txt) que quieres codificar en lzw:")
    if nombreArchivo.endswith(".txt"):
        nombreArchivo = nombreArchivo[:-4]
    nombreArchivoCompleto = nombreArchivo + ".txt"
    
    if not os.path.exists(nombreArchivoCompleto):
        print("El archivo no existe.")
        return None
    

    with open(nombreArchivoCompleto,'rb') as archivo:        
        contenido = archivo.read()
        
        for byteVal in contenido:
            
            caracter = bytes([byteVal])
            cadenaActual = cadenaSecundaria + caracter
                        
            if cadenaActual in dicc_inverso:
                cadenaSecundaria = cadenaActual
            else:
                listaCodigos.append(dicc_inverso[cadenaSecundaria])
                if tamanio < MAXIMO_NUMERO_BITS: #12 bits
                    dicc_inverso[cadenaActual] = tamanio
                    tamanio = tamanio + 1
                cadenaSecundaria = caracter
        
        if cadenaSecundaria:
                listaCodigos.append(dicc_inverso[cadenaSecundaria])
                
    dicc_inverso.clear()
    
    print("Compresión finalizada.")
    return listaCodigos, nombreArchivo


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
        print("Pulsa 1 codificar archivo (.txt)");
        print("Pulsa 2 descodificar archivo (.lzw)");
        print("Pulsa 3  para comparar dos txt")
        print("Pulsa 4  para salir\n")
        
        respuesta = input("Selecciona una opcion: ").strip()
        
        if respuesta == "1":
            codificacion()
            
        elif respuesta == "2":
            decodificacion()
           
        elif respuesta == "3":
            comparar_detallado()

        elif respuesta == "4":
            print("Saliendo del programa")
            salida = False
            
        else:
            print("\nOpción incorrecta\n\n")


if __name__ == "__main__":
    main()