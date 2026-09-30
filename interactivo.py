# interactivo.py
# Modo interactivo (REPL)
#
#   python3 main.py --interactivo
#       Escribe sentencias del lenguaje y ve el resultado al instante.
#       Las variables se conservan entre una línea y otra.
#
#   python3 main.py --interactivo --gramatica archivo.txt
#       Escribe cadenas de tokens y ve si la gramática las acepta (con traza).

from lexer     import tokenize, LexerError
from parser    import Parser, ParseError
from semantica import SemanticAnalyzer, SemanticError
from gramatica import (GRAMMAR, INICIAL, normalizar, leer_gramatica,
                       eliminar_recursion_izquierda, factorizar, analizar,
                       imprimir_gramatica, imprimir_conjuntos, imprimir_tabla,
                       print_sets, traza)


def leer_linea(prompt):
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def formato(v):
    texto = f"{v:.6f}".rstrip("0").rstrip(".")
    return "0" if texto == "-0" else texto


# ── REPL del lenguaje ─────────────────────────────────────────
AYUDA_LENGUAJE = """
  Escribe una sentencia y presiona Enter. El ';' final es opcional.
    x = 10
    y = x * 2 + sin(30)
    abs(-5) % 3
  Comandos:
    :vars        muestra la tabla de símbolos
    :conjuntos   muestra PRIMEROS, SIGUIENTES y PREDICCIÓN
    :tokens      activa / desactiva la vista de tokens
    :arbol       activa / desactiva la vista del AST
    :traza       activa / desactiva la traza con la tabla M
    :borrar      elimina todas las variables
    :ayuda       muestra esta ayuda
    :salir       termina
"""


def repl_lenguaje():
    analizador = SemanticAnalyzer()          # conserva las variables
    g = normalizar(GRAMMAR)
    tabla = analizar(g, INICIAL)["tabla"]
    ver = {"tokens": False, "arbol": False, "traza": False}

    print("=" * 70)
    print("  MODO INTERACTIVO — lenguaje de expresiones (ángulos en grados)")
    print("  Escribe :ayuda para ver los comandos, :salir para terminar")
    print("=" * 70)

    while True:
        linea = leer_linea(">>> ")
        if linea is None:
            break
        linea = linea.strip()
        if not linea:
            continue

        # ── comandos ──
        if linea.startswith(":"):
            cmd = linea[1:].lower()
            if cmd in ("salir", "q"):
                break
            elif cmd == "ayuda":
                print(AYUDA_LENGUAJE)
            elif cmd == "vars":
                analizador.print_symbol_table()
            elif cmd == "conjuntos":
                print_sets()
            elif cmd == "borrar":
                analizador.symbol_table.clear()
                print("  Variables eliminadas")
            elif cmd in ver:
                ver[cmd] = not ver[cmd]
                print(f"  {cmd}: {'activado' if ver[cmd] else 'desactivado'}")
            else:
                print("  Comando desconocido. Escribe :ayuda")
            continue

        if not linea.endswith(";"):
            linea += ";"

        # ── léxico ──
        try:
            tokens = tokenize(linea)
        except LexerError as e:
            print(f"  {e}")
            continue
        if ver["tokens"]:
            print("  Tokens:", " ".join(f"{t.type}({t.value})" for t in tokens[:-1]))
        if ver["traza"]:
            traza(g, INICIAL, tabla, [t.type for t in tokens[:-1]])

        # ── sintáctico ──
        try:
            ast = Parser(tokens).parse()
        except ParseError as e:
            print(f"  {e}")
            continue
        if ver["arbol"]:
            for stmt in ast.statements:
                print(f"  AST: {stmt}")

        # ── semántico ──
        try:
            resultados = analizador.analyze(ast)
        except SemanticError as e:
            print(f"  {e}")
            continue
        for stmt, valor in zip(ast.statements, resultados):
            nombre = getattr(stmt, "name", None)
            if nombre:                              # asignación
                print(f"  {nombre} = {formato(valor)}")
            else:
                print(f"  = {formato(valor)}")

    print("  Fin del modo interactivo")


# ── REPL de una gramática cualquiera ──────────────────────────
AYUDA_GRAMATICA = """
  Escribe una cadena de terminales separados por espacios y presiona Enter.
  El programa muestra la traza y dice si la cadena es ACEPTADA o RECHAZADA.
    Ejemplo (diapositiva 14):  cuatro dos uno
  Comandos:
    :gramatica   muestra la gramática (ya transformada)
    :conjuntos   muestra PRIMEROS, SIGUIENTES y PREDICCIÓN
    :tabla       muestra la tabla M
    :ayuda       muestra esta ayuda
    :salir       termina
"""


def repl_gramatica(ruta):
    try:
        g, inicial = leer_gramatica(ruta)
    except (OSError, ValueError) as e:
        print(f"[ERROR] {e}")
        return
    g, _ = eliminar_recursion_izquierda(g)
    g, _ = factorizar(g)
    r = analizar(g, inicial)

    print("=" * 70)
    print(f"  MODO INTERACTIVO — gramática de {ruta}")
    print("=" * 70)
    imprimir_gramatica(g)
    print()
    if r["conflictos"]:
        print("  ATENCIÓN: la gramática NO es LL(1); la tabla usa la primera")
        print("  regla de cada conflicto. Escribe :conjuntos para ver cuáles.")
    else:
        print("  La gramática ES LL(1)")
    print("  Escribe :ayuda para ver los comandos, :salir para terminar")

    while True:
        linea = leer_linea(">>> ")
        if linea is None:
            break
        linea = linea.strip()
        if not linea:
            continue
        if linea.startswith(":"):
            cmd = linea[1:].lower()
            if cmd in ("salir", "q"):
                break
            elif cmd == "ayuda":
                print(AYUDA_GRAMATICA)
            elif cmd == "gramatica":
                imprimir_gramatica(g)
            elif cmd == "conjuntos":
                imprimir_conjuntos(g, r)
            elif cmd == "tabla":
                imprimir_tabla(r)
            else:
                print("  Comando desconocido. Escribe :ayuda")
            continue

        ok = traza(g, inicial, r["tabla"], linea.split())
        print(f"  → {'CADENA ACEPTADA' if ok else 'CADENA RECHAZADA'}")

    print("  Fin del modo interactivo")
