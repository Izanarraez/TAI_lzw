# -*- coding: utf-8 -*-
"""
Created on Sun Oct 19 19:55:09 2025

@author: izana
"""

def estaEndDiccionario(cadena,diccionario):
    
    for codigo,valor in diccionario.items():
        if(cadena == valor):
            return codigo;
    
    return -1

def lzw_codificacion():
    
    dicc = { x: chr(x) for x in range(256)}
    
    cadenaActual = ""
    
    archivo = open("parteQuijote.txt",'r',encoding="utf-8")
        
    tamaño = 255
    
    for fila in archivo:
        
        for caracter in fila:
            
            cadenaActual += caracter
            
            if(estaEndDiccionario(caracter,dicc) == -1):
                
                tamaño = tamaño + 1;
                dicc[tamaño] = caracter
                cadenaActual = ""
                
            if(estaEndDiccionario(cadenaActual, dicc) == -1):
                
                tamaño = tamaño + 1;
                dicc[tamaño] = cadenaActual
                cadenaActual = ""
                    
    
    for i in range(len(dicc)):
        print(str(i)+":"+dicc[i])
    
    #return dicc
    
def main():
    
    while True:
        print("Pulsa 1 si quieres codificar un texto");
        print("Pulsa 2 si quieres decodificar un texto");
        print("Pulsa 3  para salir")
        
        respuesta = input("Selecciona una opcion:")
        
        if respuesta == "1": #Codificar
            lzw_codificacion()  
            
        if respuesta == "2": #Decodificar
            break
           
        if respuesta == "3":
            break
        
main()
