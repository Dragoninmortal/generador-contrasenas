#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de diccionarios de contraseñas (estilo CUPP) para Parrot OS / Linux.

A partir de datos personales (nombre, fecha, palabra clave, número) genera una
lista de posibles contraseñas combinando variantes, sustituciones leet, años,
números y símbolos.

Uso como módulo:
    import diccionario
    tokens = diccionario.build_tokens(nombre="Diego", palabra="azul", numero="2026",
                                      fecha=(5, 11, 1998))
    for pw in diccionario.generar(tokens, limite=100000):
        print(pw)

Uso como programa (CLI):
    python3 diccionario.py --nombre Diego --palabra azul --numero 2026 \\
                           --fecha 1998-11-05 -o palabras.txt --max 500000

AVISO: úsalo solo contra sistemas y cuentas para los que tengas autorización
explícita (tus propios equipos, laboratorios, CTF o auditorías contratadas).
"""

import argparse
import datetime
import sys

# ----------------------------------------------------------------------------
# Conjuntos base
# ----------------------------------------------------------------------------
LEET = str.maketrans({
    "a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7", "b": "8", "g": "9",
    "A": "4", "E": "3", "I": "1", "O": "0", "S": "5", "T": "7", "B": "8", "G": "9",
})

SIMBOLOS = ["!", "@", "#", "$", "%", "&", "*", ".", "_", "-", "+", "=", "?", "~", "^"]
SEPARADORES = ["", "_", ".", "-", "@", "+"]

COMUNES = [
    "1", "12", "123", "1234", "12345", "123456", "1234567", "12345678", "123456789",
    "111", "1111", "11111", "000", "0000", "007", "69", "666", "777", "888", "999",
    "100", "101", "321", "abc", "qwerty", "admin", "pass", "password", "root", "hola",
]


def _leet(s):
    return s.translate(LEET)


def _variantes(palabra):
    """Devuelve variantes de una palabra (mayúsculas, minúsculas, leet, etc.)."""
    palabra = palabra.strip()
    if not palabra:
        return []
    vs = [
        palabra,
        palabra.lower(),
        palabra.upper(),
        palabra.capitalize(),
        palabra.swapcase(),
        _leet(palabra),
        _leet(palabra.lower()),
        _leet(palabra.capitalize()),
    ]
    vistos = set()
    salida = []
    for v in vs:
        if v and v not in vistos:
            vistos.add(v)
            salida.append(v)
    return salida


# ----------------------------------------------------------------------------
# Construcción de tokens a partir de los datos
# ----------------------------------------------------------------------------
def build_tokens(nombre="", palabra="", numero="", fecha=None, anio_actual=None):
    """Devuelve un diccionario con las piezas listas para combinar."""
    anio_actual = anio_actual or datetime.date.today().year

    # --- bases (palabras) ---
    bases = []
    if nombre:
        partes = [p for p in nombre.split() if p]
        if partes:
            bases.append("".join(partes))
            bases.extend(partes)
    if palabra:
        partes = [p for p in palabra.split() if p]
        if partes:
            bases.append("".join(partes))
            bases.extend(partes)

    bases_unicas = []
    for b in bases:
        if b and b not in bases_unicas:
            bases_unicas.append(b)

    variantes = []
    for b in bases_unicas:
        for v in _variantes(b):
            if v not in variantes:
                variantes.append(v)

    # --- números ---
    nums = set()
    if numero:
        d = "".join(c for c in numero if c.isdigit())
        if d:
            nums.add(d)
            nums.add(d[::-1])
            if len(d) >= 2:
                nums.add(d[-2:])
                nums.add(d[:2])
            if len(d) >= 4:
                nums.add(d[-4:])
    nums.update(str(i) for i in range(0, 100))
    nums.update("%02d" % i for i in range(0, 100))
    nums.update(COMUNES)

    # --- años ---
    years = set()
    if fecha and fecha[2]:
        y = int(fecha[2])
        years.update([str(y), "%02d" % (y % 100), str(y - 1), str(y + 1)])
    else:
        years.update([str(anio_actual), str(anio_actual - 1), "%02d" % (anio_actual % 100)])
    years.update(str(i) for i in range(1980, anio_actual + 2))

    # --- fechas en varios formatos ---
    fechas = []
    if fecha and fecha[0] and fecha[1] and fecha[2]:
        d, m, y = int(fecha[0]), int(fecha[1]), int(fecha[2])
        yy = "%02d" % (y % 100)
        fechas = [
            "%02d%02d%02d" % (d, m, y % 100),
            "%02d%02d%d" % (d, m, y),
            "%d%02d%02d" % (y % 100, m, d),
            "%02d%02d" % (d, m),
            "%02d%02d" % (m, d),
            "%d" % y,
            yy,
        ]

    return {
        "variantes": variantes,
        "nums": sorted(nums),
        "years": sorted(years),
        "fechas": fechas,
        "bases": bases_unicas,
    }


# ----------------------------------------------------------------------------
# Motor de combinaciones
# ----------------------------------------------------------------------------
def _iter_candidatos(tokens):
    """Genera todos los candidatos (sin deduplicar), en orden de relevancia."""
    variantes = tokens["variantes"]
    nums = tokens["nums"]
    years = tokens["years"]
    fechas = tokens["fechas"]

    comunes = [n for n in COMUNES if n not in ("abc", "qwerty", "admin", "pass",
                                               "password", "root", "hola")]

    # 1) tokens sueltos
    for v in variantes:
        yield v
    for f in fechas:
        yield f

    # 2) cada variante con sufijos de números / años
    for v in variantes:
        for n in nums:
            yield v + n
        for y in years:
            yield v + y
        for f in fechas:
            yield v + f

    # 3) cada variante con símbolos (sufijo y prefijo)
    for v in variantes:
        for s in SIMBOLOS:
            yield v + s
            yield s + v

    # 4) variante + número + símbolo  (los combos más típicos)
    for v in variantes:
        for n in comunes:
            for s in ("!", "@", "#", ".", "_", "1"):
                yield v + n + s
                yield v + s + n

    # 5) prefijo numérico + variante
    for v in variantes:
        for n in comunes:
            yield n + v

    # 6) combinaciones de dos palabras
    for i, a in enumerate(variantes):
        for j, b in enumerate(variantes):
            if i == j:
                continue
            for sep in SEPARADORES:
                yield a + sep + b
            # con número/año al final
            yield a + b + "%d" % (len(a) + len(b))
        for f in fechas:
            yield a + f

    # 7) doblado y variantes con primera letra en mayúscula ya incluidas en variantes


def generar(tokens, limite=None, callback=None, callback_cada=10000):
    """Genera contraseñas únicas. Respeta `limite` si se indica."""
    vistos = set()
    total = 0
    for cand in _iter_candidatos(tokens):
        if not cand or cand in vistos:
            continue
        vistos.add(cand)
        total += 1
        yield cand
        if callback and total % callback_cada == 0:
            callback(total)
        if limite and total >= limite:
            return


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
def _parse_fecha(texto):
    if not texto:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d%m%Y"):
        try:
            dt = datetime.datetime.strptime(texto, fmt)
            return (dt.day, dt.month, dt.year)
        except ValueError:
            continue
    raise argparse.ArgumentTypeError("Fecha no válida: usa AAAA-MM-DD o DD/MM/AAAA")


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Generador de diccionarios de contraseñas (estilo CUPP).",
        epilog="Úsalo solo en sistemas para los que tengas autorización.")
    p.add_argument("--nombre", default="", help="Nombre o usuario")
    p.add_argument("--palabra", default="", help="Palabra clave o frase")
    p.add_argument("--numero", default="", help="Número o teléfono")
    p.add_argument("--fecha", type=_parse_fecha, default=None,
                   help="Fecha relevante (AAAA-MM-DD)")
    p.add_argument("-o", "--salida", default="diccionario.txt",
                   help="Archivo de salida (por defecto: diccionario.txt)")
    p.add_argument("--max", type=int, default=0,
                   help="Número máximo de contraseñas (0 = sin límite)")
    args = p.parse_args(argv)

    if not any([args.nombre, args.palabra, args.numero, args.fecha]):
        print("Introduce al menos un dato (--nombre, --palabra, --numero o --fecha).",
              file=sys.stderr)
        return 1

    tokens = build_tokens(args.nombre, args.palabra, args.numero, args.fecha)
    limite = args.max if args.max > 0 else None

    total = 0
    try:
        with open(args.salida, "w", encoding="utf-8") as f:
            for pw in generar(tokens, limite,
                              callback=lambda n: print("\rGeneradas: %d" % n,
                                                       end="", flush=True)):
                f.write(pw + "\n")
                total += 1
    except KeyboardInterrupt:
        print("\nInterrumpido por el usuario.", file=sys.stderr)

    print("\nHecho: %d contraseñas escritas en %s" % (total, args.salida))
    return 0


if __name__ == "__main__":
    sys.exit(main())
