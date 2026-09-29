# main.py
# Coordinador principal del compilador LL(1)
# Ejecuta: léxico → sintáctico → semántico
# Imprime: tokens, conjuntos FIRST/FOLLOW/Predicción, AST, tabla de símbolos, resultados

import sys
from lexer    import tokenize, LexerError
from parser   import Parser, ParseError, ProgramNode
from semantica import SemanticAnalyzer, SemanticError
from gramatica  import print_sets

def print_banner(title: str):
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)

def main():
    # ── 1. Leer código fuente ──────────────────────────────────
    if len(sys.argv) < 2:
        source_file = "programa.txt"
    else:
        source_file = sys.argv[1]

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

    # ── 2. Conjuntos formales ──────────────────────────────────
    print_banner("CONJUNTOS FIRST, FOLLOW Y PREDICCIÓN")
    print_sets()

    # ── 3. Análisis léxico ─────────────────────────────────────
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

    # ── 4. Análisis sintáctico ─────────────────────────────────
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

    # ── 5. Análisis semántico + evaluación ────────────────────
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
    print("=" * 60)
    print("  COMPILADO")
    print("=" * 60)

if __name__ == "__main__":
    main()
