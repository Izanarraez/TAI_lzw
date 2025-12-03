# -*- coding: utf-8 -*-
"""
Created on Tue Nov 18 15:50:45 2025

@author: Daniel
"""

import pickle
from bitarray import bitarray

def cargar_y_lzw_descompresion(archivo_comprimido, archivo_salida=None):
    """
    Carga un archivo comprimido con pickle y lo descomprime usando LZW
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
    Convierte un bitarray a una lista de códigos LZW con tamaño fijo
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
    Descomprime lista de códigos LZW
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
