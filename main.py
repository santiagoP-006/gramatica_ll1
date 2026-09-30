# main.py
# Coordinador principal del compilador LL(1)
#
# Modo 1 — compilar un programa del lenguaje:
#   python3 main.py [programa.txt] [--traza]
#   léxico → conjuntos (calculados) → sintáctico → semántico
#
# Modo 2 — analizar cualquier gramática (diapositivas):
#   python3 main.py --gramatica archivo.txt ["cadena a analizar"]
#   elimina recursión izquierda, factoriza, calcula conjuntos,
#   verifica LL(1), muestra la tabla M y la traza de la cadena

import sys
from lexer     import tokenize, LexerError
from parser    import Parser, ParseError
from semantica import SemanticAnalyzer, SemanticError
from gramatica import (GRAMMAR, INICIAL, normalizar, leer_gramatica,
                       eliminar_recursion_izquierda, factorizar, analizar,
                       imprimir_gramatica, imprimir_conjuntos, imprimir_tabla,
                       print_sets, traza)


def print_banner(title: str):
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


# ── Modo 2: gramática leída de un archivo ─────────────────────
def modo_gramatica(ruta, cadena):
    try:
        g, inicial = leer_gramatica(ruta)
    except (OSError, ValueError) as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    print_banner(f"GRAMÁTICA LEÍDA DE {ruta}")
    print(f"  Símbolo inicial: {inicial}")
    imprimir_gramatica(g)

    g, cambios = eliminar_recursion_izquierda(g)
    print_banner("1. ELIMINACIÓN DE RECURSIÓN IZQUIERDA")
    if cambios:
        print(f"  Se eliminó en: {', '.join(cambios)}")
        imprimir_gramatica(g)
    else:
        print("  No hay recursión izquierda inmediata")

    g, cambios = factorizar(g)
    print_banner("2. FACTORIZACIÓN POR LA IZQUIERDA")
    if cambios:
        print(f"  Se factorizó en: {', '.join(cambios)}")
        imprimir_gramatica(g)
    else:
        print("  No hay prefijos comunes")

    r = analizar(g, inicial)
    print_banner("3. PRIMEROS, SIGUIENTES Y PREDICCIÓN")
    imprimir_conjuntos(g, r)

    print_banner("4. TABLA DE ANÁLISIS")
    imprimir_tabla(r)

    if cadena is not None:
        print_banner(f"5. TRAZA DE: {cadena}")
        if r["conflictos"]:
            print("  (La gramática no es LL(1): la tabla usa la primera regla de cada conflicto)")
        ok = traza(g, inicial, r["tabla"], cadena.split())
        print(f"\n  Resultado: {'CADENA ACEPTADA' if ok else 'CADENA RECHAZADA'}")


# ── Modo 1: compilar un programa del lenguaje ─────────────────
def modo_programa(source_file, con_traza):
    try:
        with open(source_file, "r", encoding="utf-8") as f:
            source = f.read()
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo '{source_file}'")
        sys.exit(1)

    print_banner("GRAMÁTICA LL(1) — EXPRESIONES MATEMÁTICAS CON VARIABLES")
    print(f"  Archivo fuente: {source_file}")
    print()
    print("  Código fuente:")
    for i, line in enumerate(source.strip().split("\n"), 1):
        print(f"    {i:>2}: {line}")

    # ── Conjuntos calculados a partir de GRAMMAR ──────────────
    print_banner("CONJUNTOS PRIMEROS, SIGUIENTES Y PREDICCIÓN (calculados)")
    print_sets()

    # ── Fase 1: léxico ────────────────────────────────────────
    print_banner("FASE 1 — ANÁLISIS LÉXICO")
    try:
        tokens = tokenize(source)
        for tok in tokens:
            if tok.type != "$":
                print(f"  {tok}")
        print(f"\n  Total de tokens: {len(tokens) - 1}")
    except LexerError as e:
        print(f"\n  {e}")
        sys.exit(1)

    # ── Traza con la tabla M (opcional) ───────────────────────
    if con_traza:
        print_banner("TRAZA DEL ANÁLISIS PREDICTIVO (tabla M)")
        g = normalizar(GRAMMAR)
        r = analizar(g, INICIAL)
        traza(g, INICIAL, r["tabla"], [t.type for t in tokens if t.type != "$"])

    # ── Fase 2: sintáctico ────────────────────────────────────
    print_banner("FASE 2 — ANÁLISIS SINTÁCTICO (AST)")
    try:
        parser = Parser(tokens)
        ast    = parser.parse()
        for i, stmt in enumerate(ast.statements, 1):
            print(f"  Sentencia {i}: {stmt}")
        print(f"\n  Árbol AST generado")
    except ParseError as e:
        print(f"\n  {e}")
        sys.exit(1)

    # ── Fase 3: semántico ─────────────────────────────────────
    print_banner("FASE 3 — ANÁLISIS SEMÁNTICO Y EVALUACIÓN")
    try:
        analyzer = SemanticAnalyzer()
        results  = analyzer.analyze(ast)

        for i, (stmt, result) in enumerate(zip(ast.statements, results), 1):
            print(f"  Sentencia {i}: {stmt}")
            print(f"    → Resultado: {result:.6f}")
            print()

        print_banner("TABLA DE SÍMBOLOS (Variables declaradas)")
        analyzer.print_symbol_table()

    except SemanticError as e:
        print(f"\n  {e}")
        sys.exit(1)

    print()
    print("=" * 70)
    print("  COMPILADO")
    print("=" * 70)


def main():
    args = sys.argv[1:]
    if args and args[0] == "--gramatica":
        if len(args) < 2:
            print('Uso: python3 main.py --gramatica archivo.txt ["cadena"]')
            sys.exit(1)
        modo_gramatica(args[1], args[2] if len(args) > 2 else None)
    else:
        archivos = [a for a in args if not a.startswith("--")]
        modo_programa(archivos[0] if archivos else "programa.txt", "--traza" in args)


if __name__ == "__main__":
    main()
