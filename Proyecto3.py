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
from bitarray.util import int2ba, ba2int

# --- CONSTANTES ---
MAXIMO_BITS_CODIFICACION = 12
MAXIMO_NUMERO_BITS = 2**MAXIMO_BITS_CODIFICACION

# --- FUNCIONES DE ALTO NIVEL ---
def codificacion():
    """
    Ejecuta el proceso completo de compresión LZW:

    - Solicita al usuario un archivo .txt.
    - Llama a 'comprime_a_clave' para obtener los códigos LZW.
    - Llama a 'guardar_archivo_lzw' para generar el binario.

    Retorna:
        None
    """
    resultado = comprime_a_clave()
    
    if resultado:
        listaCodigos, nombreArchivoBase = resultado
        nombreSalida = nombreArchivoBase + ".lzw"
        
        guardar_archivo_lzw(nombreSalida, listaCodigos)


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
    else:
        nombreSinExtension = nombreArchivo
        nombreArchivo += ".lzw"
        
    if not os.path.exists(nombreArchivo):
        print(f"Error: El archivo {nombreArchivo} no existe.")
    else:
        nombreSalida = input("Introduce el nombre del archivo de salida (sin .txt): ").strip()
        
        if not nombreSalida: # Si no escribe nada, se pone un nombre automático
            nombreSalida = nombreSinExtension + "_descomprimido.txt"
        elif not nombreSalida.endswith(".txt"):
            nombreSalida += ".txt"
            
        # Proceso de lectura y conversión
        try:
            bits = bitarray()
            with open(nombreArchivo, 'rb') as archivo:
                bits.fromfile(archivo)
            
            codigos = bits_a_codigos(bits, MAXIMO_BITS_CODIFICACION)
            
            # Lógica de descompresión
            texto_recuperado = lzw_descompresion_core(codigos)
            
            # Guardado final
            guardar_archivo_texto(nombreSalida, texto_recuperado)
            
        except Exception as e:
            print(f"Error durante el proceso de descompresión: {e}")


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
    else:
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
                    
        except Exception as e:
            print(f"Ocurrió un error: {e}")


# --- FUNCIONES DE LÓGICA Y GESTIÓN DE FICHEROS ---

def comprime_a_clave():
    """
    Comprime el contenido de un archivo .txt usando LZW.

    Solicita el nombre del archivo al usuario.

    Retorna:
        tuple: (listaCodigos, nombreArchivo)
        None: si ocurre un error.
    """
    dicc_inverso = { bytes([x]) : x for x in range(256)} 
    cadenaActual = b""
    cadenaSecundaria = b""
    listaCodigos = []
    tamanio = 256
    resultado = None
    
    nombreArchivo = input("Introduce el nombre del archivo (sin txt) a codificar: ").strip()
    if nombreArchivo.endswith(".txt"):
        nombreArchivo = nombreArchivo[:-4]
    nombreArchivoCompleto = nombreArchivo + ".txt"
    
    if not os.path.exists(nombreArchivoCompleto):
        print("El archivo no existe.")
    else:
        try:
            with open(nombreArchivoCompleto,'rb') as archivo:        
                contenido = archivo.read()
                
                for byteVal in contenido:
                    caracter = bytes([byteVal])
                    cadenaActual = cadenaSecundaria + caracter
                                
                    if cadenaActual in dicc_inverso:
                        cadenaSecundaria = cadenaActual
                    else:
                        listaCodigos.append(dicc_inverso[cadenaSecundaria])
                        if tamanio < MAXIMO_NUMERO_BITS: # 12 bits
                            dicc_inverso[cadenaActual] = tamanio
                            tamanio = tamanio + 1
                        cadenaSecundaria = caracter
                
                if cadenaSecundaria:
                    listaCodigos.append(dicc_inverso[cadenaSecundaria])
            
            print("Compresión en memoria finalizada.")
            resultado = (listaCodigos, nombreArchivo)
            
        except Exception as e:
            print(f"Error leyendo el archivo: {e}")

    return resultado


def guardar_archivo_lzw(nombre_archivo, lista_codigos):
    """
    Convierte una lista de códigos enteros a bits y los guarda en un archivo.

    Parámetros:
        nombre_archivo (str): Ruta del archivo de salida (.lzw).
        lista_codigos (list[int]): Lista de códigos LZW a guardar.

    Retorna:
        bool: True si se guardó correctamente, False si hubo error.
    """
    exito = False
    
    try:
        bits = bitarray()
        
        # Convertimos cada código a su representación de 12 bits
        for codigo in lista_codigos:
            bits.extend(int2ba(codigo, length=MAXIMO_BITS_CODIFICACION))
            
        with open(nombre_archivo, 'wb') as archivo:
            bits.tofile(archivo)
            
        print(f"\nArchivo comprimido guardado exitosamente: {nombre_archivo}")
        exito = True
        
    except OSError as error:
        print(f"Error al guardar el archivo comprimido: {error}")
        
    return exito


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


def lzw_descompresion_core(codigos):
    """
    Descomprime una lista de códigos mediante el algoritmo LZW.

    Parámetros:
        codigos (list[int]): lista de códigos LZW.

    Retorna:
        bytes: texto reconstruido.
    """
    resultado_bytes = b""
    
    if codigos:
        diccionario = {i: bytes([i]) for i in range(256)}
        proximo_codigo = 256
        buffer_salida = bytearray()
        
        # Primer código
        codigo_anterior = codigos[0]
        cadena_anterior = diccionario[codigo_anterior]
        buffer_salida.extend(cadena_anterior)
        
        # Procesar resto de códigos
        for codigo_actual in codigos[1:]:
            entrada_actual = b""
            
            # 1. Decodificar
            if codigo_actual in diccionario:
                entrada_actual = diccionario[codigo_actual]
            elif codigo_actual == proximo_codigo:
                entrada_actual = cadena_anterior + bytes([cadena_anterior[0]])
            
            # Si la entrada es válida, procesamos
            if entrada_actual:
                buffer_salida.extend(entrada_actual)
                
                # 2. Actualizar diccionario (si cabe)
                if proximo_codigo < MAXIMO_NUMERO_BITS:
                    nueva_entrada = cadena_anterior + bytes([entrada_actual[0]])
                    diccionario[proximo_codigo] = nueva_entrada
                    proximo_codigo += 1
                
                cadena_anterior = entrada_actual
            
        resultado_bytes = bytes(buffer_salida)

    return resultado_bytes


def guardar_archivo_texto(nombre_archivo, contenido_bytes):
    """
    Guarda el contenido binario (texto recuperado) en un archivo.

    Parámetros:
        nombre_archivo (str): Ruta del archivo de salida (.txt).
        contenido_bytes (bytes): Texto a escribir.

    Retorna:
        bool: True si se guardó correctamente, False si hubo error.
    """
    exito = False
    
    try:
        with open(nombre_archivo, 'wb') as archivo:
            archivo.write(contenido_bytes)
        print(f"\nArchivo descomprimido guardado: {nombre_archivo}")
        exito = True
        
    except OSError as error:
        print(f"Error al guardar el archivo de texto: {error}")
        
    return exito


# --- PROGRAMA PRINCIPAL ---

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
        print("\n---MENÚ PRINCIPAL---\n")
        print("Pulsa 1 codificar archivo (.txt)")
        print("Pulsa 2 descodificar archivo (.lzw)")
        print("Pulsa 3 para comparar dos txt")
        print("Pulsa 4 para salir\n")
        
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