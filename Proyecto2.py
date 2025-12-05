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

import difflib
import os
from bitarray import bitarray
from bitarray.util import int2ba
from bitarray.util import ba2int

MAXIMO_BITS_CODIFICACION = 12
MAXIMO_NUMERO_BITS = 2**MAXIMO_BITS_CODIFICACION

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
       
def codificacion():
    
    """
    Ejecuta el proceso de codificación LZW.
    """
     
    resultado = comprime_a_clave()
    
    if not resultado:
        print("No se generaron códigos o hubo un error.")
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
     
    
'''
def guardar_archivo_lzw(codigos, nombre_salida):
    """
    Convierte la lista de enteros (códigos) en bits y los guarda en un archivo.
    No usa pickle. Usa bitarray para empaquetar 12 bits por código.
    """
    bits = bitarray()
    
    # Convertimos cada entero en 12 bits
    for codigo in codigos:
        # int2ba convierte entero a bitarray
        bits.extend(int2ba(codigo, length=MAXIMO_BITS_CODIFICACION))
    
    try:
        with open(nombre_salida, 'wb') as f:
            # Escribimos los bits directamente al archivo
            bits.tofile(f)
        print(f"Archivo comprimido guardado en: {nombre_salida}")
    except Exception as e:
        print(f"Error guardando archivo: {e}")
        
'''
      
def decodificacion():
    """
    Ejecuta el proceso de descompresión LZW.
    
    Solicita al usuario el archivo comprimido (.lzw) y el nombre del archivo 
    de salida. Llama a 'cargar_y_lzw_descompresion()' para reconstruir el 
    contenido original y guardarlo en un archivo .txt.
    """
    
    nombreArchivo = input("Introduce el nombre del archivo comprimido (sin .lzw): ").strip()

    if nombreArchivo.endswith(".lzw"):
        nombreSinExtension = nombreArchivo[:-4]
        
    nombreSalida = input("Introduce el nombre del archivo de salida (sin .txt): ").strip()
    
    if nombreSalida == "": # Si no escribe nada, se pone un nombre automático
        nombreSalida = nombreSinExtension + "_descomprimido.txt"
    else:
        if nombreSalida.endswith(".txt"):
            nombreSalida = nombreSalida[:-4]
        nombreSalida += ".txt"
    
    # Ejecutar descompresión
    textoBytes = cargar_y_lzw_descompresion(nombreArchivo + ".lzw", nombreSalida)
    
    if textoBytes is None:
        print("No se pudo descomprimir el archivo.")
    
    
    
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

    for i in range(0, len(bits), longitud_codigo):
        chunk = bits[i:i+longitud_codigo]
        if len(chunk) == longitud_codigo:
            codigos.append(ba2int(chunk))

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

    dicc_inverso = { bytes([x]) : x for x in range(256)} #poner valor en listaCodigos
    
    cadenaActual = b""
    cadenaSecundaria = b""
    
    listaCodigos = []
    
    tamanio = 256
    
    nombreArchivo = input("Introduce el nombre del archivo que quieres codificar en lzw:")
    
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

#Comparador de tos documentos para ver si son iguales
def comparar_detallado():
    """
    Compara dos archivos byte a byte.
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
                
                # Opcional: mostrar dónde difieren (solo primeros bytes para no saturar)
                diferencias = 0
                for i, (b1, b2) in enumerate(zip(contenido1, contenido2)):
                    if b1 != b2:
                        print(f"Primera diferencia en el byte {i}: Original={b1}, Nuevo={b2}")
                        break
                    
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    main()