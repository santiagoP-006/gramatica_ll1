# gramatica.py
# Gramática LL(1) del lenguaje y ALGORITMOS que calculan, a partir de ella:
#   PRIMEROS, SIGUIENTES, PREDICCIÓN, verificación LL(1) y tabla M.
# También sirve para cualquier otra gramática leída desde un archivo .txt:
#   eliminación de recursión izquierda, factorización y traza del análisis.

EPS = "ε"
FIN = "$"

# ── Gramática del lenguaje ────────────────────────────────────
# Una producción vacía se escribe ["ε"]
GRAMMAR = {
    "programa": [
        ["sentencia", "programa"],
        ["ε"]
    ],
    # Factorización por la izquierda: cada sentencia arranca con un token distinto
    "sentencia": [
        ["ID",     "resto_sent", "SEMICOLON"],
        ["NUM",    "term'", "expr'", "SEMICOLON"],
        ["MINUS",  "factor", "term'", "expr'", "SEMICOLON"],
        ["ABS",    "LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],
        ["SIN",    "LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],
        ["COS",    "LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],
        ["TAN",    "LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],
        ["ATAN",   "LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],
        ["LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],
    ],
    # Con ASIG es asignación; si no, es una expresión que empezó con ID
    "resto_sent": [
        ["ASIG", "expr"],
        ["term'", "expr'"]
    ],
    "expr": [
        ["term", "expr'"]
    ],
    "expr'": [
        ["PLUS",  "term", "expr'"],
        ["MINUS", "term", "expr'"],
        ["ε"]
    ],
    "term": [
        ["factor", "term'"]
    ],
    "term'": [
        ["MULT", "factor", "term'"],
        ["DIV",  "factor", "term'"],
        ["MOD",  "factor", "term'"],
        ["ε"]
    ],
    "factor": [
        ["LPAREN", "expr", "RPAREN"],
        ["MINUS",  "factor"],
        ["ABS",    "LPAREN", "expr", "RPAREN"],
        ["SIN",    "LPAREN", "expr", "RPAREN"],
        ["COS",    "LPAREN", "expr", "RPAREN"],
        ["TAN",    "LPAREN", "expr", "RPAREN"],
        ["ATAN",   "LPAREN", "expr", "RPAREN"],
        ["NUM"],
        ["ID"]
    ]
}
INICIAL = "programa"


# ── Utilidades ────────────────────────────────────────────────
def normalizar(g):
    """Copia la gramática y convierte ["ε"] en [] (producción vacía)."""
    return {A: [[s for s in alt if s != EPS] for alt in alts] for A, alts in g.items()}


def es_terminal(g, x):
    return x not in g


def texto_prod(A, alfa):
    return f"{A} → {' '.join(alfa) if alfa else EPS}"


def texto_conj(conjunto):
    return "{ " + ", ".join(sorted(conjunto, key=lambda s: (s == EPS, s == FIN, s))) + " }"


def nombre_nuevo(g, A):
    """Nombre para un no terminal nuevo: A', A'', ..."""
    nuevo = A + "'"
    while nuevo in g:
        nuevo += "'"
    return nuevo


# ── Leer una gramática desde un archivo de texto ─────────────
# Formato:   A -> x B | y | ε        (una o varias líneas por no terminal)
#            | z                      (continuación del no terminal anterior)
#            # comentario
# El símbolo inicial es el lado izquierdo de la primera regla.
def leer_gramatica(ruta):
    g, inicial, actual = {}, None, None
    with open(ruta, encoding="utf-8") as f:
        for num, linea in enumerate(f, 1):
            linea = linea.split("#", 1)[0].strip().replace("→", "->")
            if not linea:
                continue
            if "->" in linea:
                izq, der = linea.split("->", 1)
                actual = izq.strip()
                if not actual or " " in actual:
                    raise ValueError(f"Línea {num}: lado izquierdo inválido")
                if inicial is None:
                    inicial = actual
            elif linea.startswith("|") and actual:
                der = linea[1:]
            else:
                raise ValueError(f"Línea {num}: falta '->'")
            for alt in der.split("|"):
                simbolos = [s for s in alt.split() if s not in (EPS, "eps")]
                g.setdefault(actual, []).append(simbolos)
    if not g:
        raise ValueError("La gramática está vacía")
    return g, inicial


# ── Eliminar recursión izquierda inmediata ───────────────────
# A → Aα1 | ... | Aαm | β1 | ... | βn   ⇒   A → β1 A' | ... | βn A'
#                                             A' → α1 A' | ... | αm A' | ε
def eliminar_recursion_izquierda(g):
    nueva, cambios = {}, []
    for A, alts in g.items():
        alfas = [alt[1:] for alt in alts if alt and alt[0] == A]
        betas = [alt for alt in alts if not alt or alt[0] != A]
        if not alfas or not betas:
            nueva[A] = [list(a) for a in alts]
            continue
        A2 = nombre_nuevo({**g, **nueva}, A)
        nueva[A] = [b + [A2] for b in betas]
        nueva[A2] = [a + [A2] for a in alfas] + [[]]
        cambios.append(A)
    return nueva, cambios


# ── Factorizar por la izquierda ──────────────────────────────
# A → αβ1 | αβ2   ⇒   A → αA'   y   A' → β1 | β2
def prefijo_comun(listas):
    prefijo = []
    for simbolos in zip(*listas):
        if len(set(simbolos)) != 1:
            break
        prefijo.append(simbolos[0])
    return prefijo


def factorizar(g):
    g = {A: [list(a) for a in alts] for A, alts in g.items()}
    cambios = []
    hubo_cambio = True
    while hubo_cambio:
        hubo_cambio = False
        for A in list(g):
            grupos = {}
            for alt in g[A]:
                if alt:
                    grupos.setdefault(alt[0], []).append(alt)
            for grupo in grupos.values():
                if len(grupo) < 2:
                    continue
                prefijo = prefijo_comun(grupo)
                A2 = nombre_nuevo(g, A)
                nuevas, puesta = [], False
                for alt in g[A]:
                    if alt in grupo:
                        if not puesta:
                            nuevas.append(prefijo + [A2])
                            puesta = True
                    else:
                        nuevas.append(alt)
                # insertar A' justo después de A para conservar el orden
                g2 = {}
                for X, alts in g.items():
                    g2[X] = nuevas if X == A else alts
                    if X == A:
                        g2[A2] = [alt[len(prefijo):] for alt in grupo]
                g = g2
                cambios.append(A)
                hubo_cambio = True
                break
            if hubo_cambio:
                break
    return g, cambios


# ── PRIMEROS ──────────────────────────────────────────────────
def primeros_cadena(g, primeros, alfa):
    resultado = set()
    for x in alfa:
        if es_terminal(g, x):
            resultado.add(x)
            return resultado
        resultado |= primeros[x] - {EPS}
        if EPS not in primeros[x]:
            return resultado
    resultado.add(EPS)          # todos pueden ser vacíos (o alfa es ε)
    return resultado


def calcular_primeros(g):
    primeros = {A: set() for A in g}
    cambio = True
    while cambio:                               # iteración de punto fijo
        cambio = False
        for A, alts in g.items():
            for alfa in alts:
                antes = len(primeros[A])
                primeros[A] |= primeros_cadena(g, primeros, alfa)
                cambio |= len(primeros[A]) != antes
    return primeros


# ── SIGUIENTES ────────────────────────────────────────────────
def calcular_siguientes(g, inicial, primeros):
    siguientes = {A: set() for A in g}
    siguientes[inicial].add(FIN)
    cambio = True
    while cambio:
        cambio = False
        for A, alts in g.items():
            for alfa in alts:
                for i, B in enumerate(alfa):
                    if es_terminal(g, B):
                        continue
                    antes = len(siguientes[B])
                    beta = primeros_cadena(g, primeros, alfa[i + 1:])
                    siguientes[B] |= beta - {EPS}
                    if EPS in beta:                 # B al final o β anulable
                        siguientes[B] |= siguientes[A]
                    cambio |= len(siguientes[B]) != antes
    return siguientes


# ── PREDICCIÓN ────────────────────────────────────────────────
# PRED(A → α) = PRIMEROS(α) - {ε}  ∪  SIGUIENTES(A) si ε ∈ PRIMEROS(α)
def calcular_prediccion(g, primeros, siguientes):
    pred = []
    for A, alts in g.items():
        for alfa in alts:
            f = primeros_cadena(g, primeros, alfa)
            p = f - {EPS}
            if EPS in f:
                p |= siguientes[A]
            pred.append((A, alfa, p))
    return pred


# ── Verificación LL(1) y tabla M ──────────────────────────────
def verificar_ll1(pred):
    conflictos = []
    for i in range(len(pred)):
        for j in range(i + 1, len(pred)):
            if pred[i][0] == pred[j][0]:
                comun = pred[i][2] & pred[j][2]
                if comun:
                    conflictos.append((pred[i], pred[j], comun))
    return conflictos


def construir_tabla(pred):
    tabla = {}
    for A, alfa, p in pred:
        for a in p:
            tabla.setdefault((A, a), alfa)      # si hay conflicto queda la primera
    return tabla


def analizar(g, inicial):
    """Calcula todo y lo devuelve en un diccionario."""
    primeros = calcular_primeros(g)
    siguientes = calcular_siguientes(g, inicial, primeros)
    pred = calcular_prediccion(g, primeros, siguientes)
    return {
        "primeros": primeros,
        "siguientes": siguientes,
        "pred": pred,
        "conflictos": verificar_ll1(pred),
        "tabla": construir_tabla(pred),
    }


# ── Impresión ─────────────────────────────────────────────────
def imprimir_gramatica(g):
    for A, alts in g.items():
        for alfa in alts:
            print(f"  {texto_prod(A, alfa)}")


def imprimir_conjuntos(g, r):
    ancho = max(len(A) for A in g)
    print("  PRIMEROS")
    for A in g:
        print(f"    PRIMEROS({A:<{ancho}}) = {texto_conj(r['primeros'][A])}")
    print()
    print("  SIGUIENTES")
    for A in g:
        print(f"    SIGUIENTES({A:<{ancho}}) = {texto_conj(r['siguientes'][A])}")
    print()
    print("  PREDICCIÓN")
    ancho_p = max(len(texto_prod(A, a)) for A, a, _ in r["pred"])
    for n, (A, alfa, p) in enumerate(r["pred"], 1):
        print(f"    {n:>2}. PRED({texto_prod(A, alfa):<{ancho_p}}) = {texto_conj(p)}")
    print()
    print("  VERIFICACIÓN LL(1)")
    if r["conflictos"]:
        for (A, a1, _), (_, a2, _), comun in r["conflictos"]:
            print(f"    CONFLICTO en {A}: '{texto_prod(A, a1)}' y "
                  f"'{texto_prod(A, a2)}' comparten {texto_conj(comun)}")
        print("    RESULTADO: la gramática NO es LL(1)")
    else:
        print("    Los PRED de cada no terminal son disjuntos")
        print("    RESULTADO: la gramática ES LL(1)")


def imprimir_tabla(r):
    print("  TABLA DE ANÁLISIS M[no terminal, token]")
    for (A, a), alfa in r["tabla"].items():
        print(f"    M[{A}, {a}] = {texto_prod(A, alfa)}")


def print_sets(g=GRAMMAR, inicial=INICIAL):
    """Calcula y muestra los conjuntos de la gramática del lenguaje."""
    g = normalizar(g)
    imprimir_conjuntos(g, analizar(g, inicial))


# ── Traza del analizador predictivo (pila + tabla M) ─────────
def traza(g, inicial, tabla, tokens):
    """tokens: lista de terminales, sin el $ final. Devuelve True si acepta."""
    pila = [FIN, inicial]
    entrada = list(tokens) + [FIN]
    i, paso = 0, 1
    print(f"    {'Paso':<5} {'Pila':<32} {'Entrada':<32} Acción")
    while True:
        X, a = pila[-1], entrada[i]
        txt_pila = " ".join(reversed(pila))
        txt_ent = " ".join(entrada[i:])
        if len(txt_ent) > 30:
            txt_ent = txt_ent[:27] + "..."
        if len(txt_pila) > 30:
            txt_pila = txt_pila[:27] + "..."
        if X == FIN:
            accion = "aceptación" if a == FIN else f"ERROR: sobran tokens ('{a}')"
        elif es_terminal(g, X):
            accion = f"consumir {a}" if X == a else f"ERROR: se esperaba '{X}' y llegó '{a}'"
        elif (X, a) in tabla:
            accion = texto_prod(X, tabla[(X, a)])
        else:
            accion = f"ERROR: no hay regla M[{X}, {a}]"
        print(f"    {paso:<5} {txt_pila:<32} {txt_ent:<32} {accion}")
        if accion.startswith("ERROR"):
            return False
        if X == FIN:
            return True
        pila.pop()
        if es_terminal(g, X):
            i += 1
        else:
            pila.extend(reversed(tabla[(X, a)]))
        paso += 1
