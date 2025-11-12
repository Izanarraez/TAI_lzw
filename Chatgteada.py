# -*- coding: utf-8 -*-
"""
Editor de Spyder

Este es un archivo temporal.
"""
# Código ejecutado en el entorno: implementación LZW (12 bits), escritura/lectura a ficheros binarios
# Incluye BitWriter/BitReader (uso de bitarrays "casero"), compresión/descompresión de ficheros,
# cabecera en el fichero comprimido y pruebas con 5 ficheros generados localmente.
# Al final muestra una tabla con tamaños y ratios y guarda los ficheros comprimidos y descomprimidos en /mnt/data.

import os
from pathlib import Path
import struct
import random
import pandas as pd

# -------------------- Bit writer / reader (bitarray-like casero) --------------------
class BitWriter:
    def __init__(self):
        self.bytes = bytearray()
        self.cur = 0  # current byte being filled (0-255)
        self.nbits = 0  # number of bits currently in cur (0-8)
    
    def writebits(self, value, width):
        """Escribe 'width' bits del valor (0..2**width-1), big-endian dentro de esos width bits."""
        if width <= 0:
            return
        for i in range(width-1, -1, -1):
            bit = (value >> i) & 1
            self.cur = (self.cur << 1) | bit
            self.nbits += 1
            if self.nbits == 8:
                self.bytes.append(self.cur)
                self.cur = 0
                self.nbits = 0
    
    def get_bytes(self):
        padding = 0
        if self.nbits > 0:
            # left-shift remaining bits to fill byte (we've been adding MSB-first)
            self.cur = self.cur << (8 - self.nbits)
            self.bytes.append(self.cur)
            padding = 8 - self.nbits
        return bytes(self.bytes), padding

class BitReader:
    def __init__(self, data_bytes):
        self.data = data_bytes
        self.pos = 0  # index in bytes
        self.bit_pos = 0  # bit position inside current byte (0..7) - msb first
    
    def readbits(self, width):
        if width <= 0:
            return 0
        value = 0
        for _ in range(width):
            if self.pos >= len(self.data):
                raise EOFError("No more bits available")
            current_byte = self.data[self.pos]
            bit = (current_byte >> (7 - self.bit_pos)) & 1
            value = (value << 1) | bit
            self.bit_pos += 1
            if self.bit_pos == 8:
                self.bit_pos = 0
                self.pos += 1
        return value

# -------------------- LZW sobre bytes (max_bits configurable) --------------------
def lzw_encode_bytes(data: bytes, max_bits=12):
    max_table_size = 1 << max_bits
    # Inicial diccionario: 0..255 (cada símbolo es un byte)
    dict_size = 256
    dictionary = {bytes([i]): i for i in range(dict_size)}
    w = b""
    result_codes = []
    for b in data:
        c = bytes([b])
        wc = w + c
        if wc in dictionary:
            w = wc
        else:
            # emitir código de w
            result_codes.append(dictionary[w])
            # añadir wc al diccionario si hay espacio
            if dict_size < max_table_size:
                dictionary[wc] = dict_size
                dict_size += 1
            w = c
    if w:
        result_codes.append(dictionary[w])
    return result_codes

def lzw_decode_codes(codes, max_bits=12):
    max_table_size = 1 << max_bits
    dict_size = 256
    dictionary = {i: bytes([i]) for i in range(dict_size)}
    result = bytearray()
    prev_code = None
    for code in codes:
        if code in dictionary:
            entry = dictionary[code]
        elif code == dict_size:
            # caso KwKwK especial
            entry = dictionary[prev_code] + dictionary[prev_code][:1]
        else:
            raise ValueError("Código inválido durante la decodificación: %d" % code)
        result.extend(entry)
        if prev_code is not None and dict_size < max_table_size:
            dictionary[dict_size] = dictionary[prev_code] + entry[:1]
            dict_size += 1
        prev_code = code
    return bytes(result)

# -------------------- Empaquetado de códigos en bitstream --------------------
def pack_codes_to_bytes(codes, max_bits=12):
    bw = BitWriter()
    for code in codes:
        bw.writebits(code, max_bits)
    data_bytes, padding = bw.get_bytes()
    return data_bytes, padding

def unpack_bytes_to_codes(data_bytes, n_codes, max_bits=12):
    br = BitReader(data_bytes)
    codes = []
    for _ in range(n_codes):
        try:
            c = br.readbits(max_bits)
        except EOFError:
            break
        codes.append(c)
    return codes

# -------------------- Formato de fichero comprimido --------------------
# Cabecera (todos los enteros en big-endian):
# 4 bytes: magic b'LZW1'
# 8 bytes: original size (unsigned long long)
# 1 byte: max_bits (e.g., 12)
# 1 byte: padding_bits (0..7)
# 4 bytes: n_codes (unsigned int)  <-- número de códigos escritos (útil para leer exactamente)
# seguidamente: stream de bytes con los códigos empaquetados

MAGIC = b'LZW1'

def compress_file(input_path, output_path, max_bits=12):
    data = Path(input_path).read_bytes()
    codes = lzw_encode_bytes(data, max_bits=max_bits)
    packed_bytes, padding = pack_codes_to_bytes(codes, max_bits=max_bits)
    # construir cabecera
    header = bytearray()
    header.extend(MAGIC)
    header.extend(struct.pack(">Q", len(data)))  # original size 8 bytes
    header.extend(struct.pack("B", max_bits))
    header.extend(struct.pack("B", padding))
    header.extend(struct.pack(">I", len(codes)))
    # escribir fichero
    Path(output_path).write_bytes(bytes(header) + packed_bytes)
    return {
        "input_size": len(data),
        "output_size": len(header) + len(packed_bytes),
        "n_codes": len(codes),
        "padding": padding
    }

def decompress_file(input_path, output_path):
    b = Path(input_path).read_bytes()
    if len(b) < 4 or b[:4] != MAGIC:
        raise ValueError("Fichero no es un comprimido LZW válido (magic mismatch)")
    offset = 4
    orig_size = struct.unpack_from(">Q", b, offset)[0]; offset += 8
    max_bits = struct.unpack_from("B", b, offset)[0]; offset += 1
    padding = struct.unpack_from("B", b, offset)[0]; offset += 1
    n_codes = struct.unpack_from(">I", b, offset)[0]; offset += 4
    packed = b[offset:]
    # calcular número exacto de códigos si n_codes está presente (lo está)
    codes = unpack_bytes_to_codes(packed, n_codes, max_bits=max_bits)
    decoded = lzw_decode_codes(codes, max_bits=max_bits)
    Path(output_path).write_bytes(decoded)
    return {
        "orig_size": orig_size,
        "decoded_size": len(decoded),
        "n_codes": len(codes),
        "max_bits": max_bits,
        "padding": padding
    }

# -------------------- Pruebas con 5 ficheros distintos generados --------------------
out_dir = Path("/mnt/data/lzw_tests")
out_dir.mkdir(parents=True, exist_ok=True)

test_files = []

# 1) Texto corto repetitivo
t1 = out_dir / "test1_repet_text.txt"
t1.write_text("ABABABAABABA" * 100)
test_files.append(t1)

# 2) Texto largo con lenguaje natural (simulado repeticiones)
t2 = out_dir / "test2_long_text.txt"
t2.write_text(("En un lugar de La Mancha, de cuyo nombre no quiero acordarme. " * 200))
test_files.append(t2)

# 3) Binario repetitivo (imitando partes de imagen con grandes áreas iguales)
t3 = out_dir / "test3_repet_binary.bin"
t3.write_bytes(bytes([0x00]*1024 + [0xFF]*1024 + [0x00]*1024))
test_files.append(t3)

# 4) Aleatorio (difícil de comprimir)
t4 = out_dir / "test4_random.bin"
random_bytes = bytes(random.getrandbits(8) for _ in range(4096))
t4.write_bytes(random_bytes)
test_files.append(t4)

# 5) Mix: cabecera tipo imagen + patrón
t5 = out_dir / "test5_pattern_image_like.bin"
hdr = b'BM' + bytes([0]*10)  # pequeño parecido a BMP header (no válido como imagen real)
body = (b'\x10\x20\x30\x40' * 500) + (b'\x00'*800)
t5.write_bytes(hdr + body)
test_files.append(t5)

results = []
for path in test_files:
    comp_path = path.with_suffix(path.suffix + ".lzw")
    decomp_path = path.with_suffix(path.suffix + ".decompressed")
    info_comp = compress_file(path, comp_path, max_bits=12)
    info_decomp = decompress_file(comp_path, decomp_path)
    # verificar igualdad
    original = path.read_bytes()
    decompressed = decomp_path.read_bytes()
    ok = original == decompressed
    ratio = info_comp["output_size"] / info_comp["input_size"] if info_comp["input_size"]>0 else None
    results.append({
        "file": path.name,
        "original_bytes": info_comp["input_size"],
        "compressed_bytes": info_comp["output_size"],
        "ratio (compressed/orig)": ratio,
        "n_codes": info_comp["n_codes"],
        "padding_bits": info_comp["padding"],
        "decompressed_ok": ok,
        "comp_path": str(comp_path),
        "decomp_path": str(decomp_path)
    })

# Mostrar tabla con resultados
df = pd.DataFrame(results)
# Usar display helper si está disponible (se recomienda por la herramienta)
try:
    from caas_jupyter_tools import display_dataframe_to_user
    display_dataframe_to_user("Resultados LZW (12 bits)", df)
except Exception:
    pass

# También guardar CSV con resultados
csv_path = out_dir / "lzw_results.csv"
df.to_csv(csv_path, index=False)

# Imprimir resumen para que la salida sea visible en el notebook
print(df.to_string(index=False))

# Proveer rutas de descarga
generated_files = [r["comp_path"] for r in results] + [r["decomp_path"] for r in results] + [str(csv_path)]
print("\nFicheros generados (descarga):")
for f in generated_files:
    print(f"file://{f}")

# Retornar variables para inspección por el sistema
{"results": results, "out_dir": str(out_dir)}

