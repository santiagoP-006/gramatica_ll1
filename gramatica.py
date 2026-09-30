# gramatica.py
# Módulo de documentación de la gramática LL(1) ESTRICTA
# Corrección: sentencia factorizada con resto_sent para eliminar conflicto LL(1)

GRAMMAR = {
    "programa": [
        ["sentencia", "programa"],
        ["ε"]
    ],
    # Factorización por la izquierda: sentencia arranca con token único
    "sentencia": [
        ["ID",     "resto_sent",                        "SEMICOLON"],
        ["NUM",    "term'", "expr'",                    "SEMICOLON"],
        ["MINUS",  "factor", "term'", "expr'",          "SEMICOLON"],
        ["ABS",    "LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],
        ["SIN",    "LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],
        ["COS",    "LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],
        ["TAN",    "LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],
        ["LPAREN", "expr",   "RPAREN", "term'", "expr'","SEMICOLON"],
    ],
    # resto_sent resuelve el conflicto: con ASIG es asignación, si no es expr
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
        ["NUM"],
        ["ID"]
    ]
}

# ── FIRST ─────────────────────────────────────────────────────
FIRST = {
    "programa":   {"ID", "NUM", "MINUS", "ABS", "SIN", "COS", "TAN", "LPAREN", "ε"},
    "sentencia":  {"ID", "NUM", "MINUS", "ABS", "SIN", "COS", "TAN", "LPAREN"},
    "resto_sent": {"ASIG", "MULT", "DIV", "MOD", "PLUS", "MINUS",
                   "SEMICOLON", "RPAREN", "$", "ε"},
    "expr":       {"ID", "NUM", "MINUS", "ABS", "SIN", "COS", "TAN", "LPAREN"},
    "expr'":      {"PLUS", "MINUS", "ε"},
    "term":       {"ID", "NUM", "MINUS", "ABS", "SIN", "COS", "TAN", "LPAREN"},
    "term'":      {"MULT", "DIV", "MOD", "ε"},
    "factor":     {"LPAREN", "MINUS", "ABS", "SIN", "COS", "TAN", "NUM", "ID"}
}

# ── FOLLOW ────────────────────────────────────────────────────
FOLLOW = {
    "programa":   {"$"},
    "sentencia":  {"ID", "NUM", "MINUS", "ABS", "SIN", "COS", "TAN", "LPAREN", "$"},
    "resto_sent": {"SEMICOLON"},
    "expr":       {"SEMICOLON", "RPAREN", "$"},
    "expr'":      {"SEMICOLON", "RPAREN", "$"},
    "term":       {"PLUS", "MINUS", "SEMICOLON", "RPAREN", "$"},
    "term'":      {"PLUS", "MINUS", "SEMICOLON", "RPAREN", "$"},
    "factor":     {"MULT", "DIV", "MOD", "PLUS", "MINUS", "SEMICOLON", "RPAREN", "$"}
}

# ── Conjuntos de Predicción ───────────────────────────────────
# PREDICT(A → α) = FIRST(α) si ε ∉ FIRST(α)
#                  FIRST(α) ∪ FOLLOW(A) si ε ∈ FIRST(α)
PREDICT = {
    # programa
    ("programa", "sentencia programa"): {"ID","NUM","MINUS","ABS","SIN","COS","TAN","LPAREN"},
    ("programa", "ε"):                  {"$"},

    # sentencia — un token de anticipación único por regla ✓
    ("sentencia", "ID resto_sent ;"):             {"ID"},
    ("sentencia", "NUM term' expr' ;"):           {"NUM"},
    ("sentencia", "MINUS factor term' expr' ;"):  {"MINUS"},
    ("sentencia", "ABS(...) term' expr' ;"):      {"ABS"},
    ("sentencia", "SIN(...) term' expr' ;"):      {"SIN"},
    ("sentencia", "COS(...) term' expr' ;"):      {"COS"},
    ("sentencia", "TAN(...) term' expr' ;"):      {"TAN"},
    ("sentencia", "( expr ) term' expr' ;"):      {"LPAREN"},

    # resto_sent — SIN intersección ✓
    ("resto_sent", "ASIG expr"):  {"ASIG"},
    ("resto_sent", "term' expr'"): {"MULT","DIV","MOD",          # FIRST(term') sin ε
                                    "PLUS","MINUS","SEMICOLON"},  # FOLLOW(resto_sent) por term'→ε

    # expr
    ("expr", "term expr'"): {"ID","NUM","MINUS","ABS","SIN","COS","TAN","LPAREN"},

    # expr'
    ("expr'", "+ term expr'"):  {"PLUS"},
    ("expr'", "- term expr'"):  {"MINUS"},
    ("expr'", "ε"):             {"SEMICOLON", "RPAREN", "$"},

    # term
    ("term", "factor term'"): {"ID","NUM","MINUS","ABS","SIN","COS","TAN","LPAREN"},

    # term'
    ("term'", "* factor term'"): {"MULT"},
    ("term'", "/ factor term'"): {"DIV"},
    ("term'", "% factor term'"): {"MOD"},
    ("term'", "ε"):              {"PLUS","MINUS","SEMICOLON","RPAREN","$"},

    # factor
    ("factor", "( expr )"):        {"LPAREN"},
    ("factor", "- factor"):        {"MINUS"},
    ("factor", "abs( expr )"):     {"ABS"},
    ("factor", "sin( expr )"):     {"SIN"},
    ("factor", "cos( expr )"):     {"COS"},
    ("factor", "tan( expr )"):     {"TAN"},
    ("factor", "NUM"):             {"NUM"},
    ("factor", "ID"):              {"ID"},
}

# ── Tabla de parsing M[no_terminal, token] ────────────────────
PARSING_TABLE = {
    ("programa",  "ID"):      ["sentencia", "programa"],
    ("programa",  "NUM"):     ["sentencia", "programa"],
    ("programa",  "MINUS"):   ["sentencia", "programa"],
    ("programa",  "ABS"):     ["sentencia", "programa"],
    ("programa",  "SIN"):     ["sentencia", "programa"],
    ("programa",  "COS"):     ["sentencia", "programa"],
    ("programa",  "TAN"):     ["sentencia", "programa"],
    ("programa",  "LPAREN"):  ["sentencia", "programa"],
    ("programa",  "$"):       ["ε"],

    ("sentencia", "ID"):      ["ID",     "resto_sent", "SEMICOLON"],
    ("sentencia", "NUM"):     ["NUM",    "term'", "expr'", "SEMICOLON"],
    ("sentencia", "MINUS"):   ["MINUS",  "factor", "term'", "expr'", "SEMICOLON"],
    ("sentencia", "ABS"):     ["ABS",    "LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],
    ("sentencia", "SIN"):     ["SIN",    "LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],
    ("sentencia", "COS"):     ["COS",    "LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],
    ("sentencia", "TAN"):     ["TAN",    "LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],
    ("sentencia", "LPAREN"):  ["LPAREN", "expr", "RPAREN", "term'", "expr'", "SEMICOLON"],

    # resto_sent — sin conflicto: ASIG vs {MULT,DIV,MOD,PLUS,MINUS,SEMICOLON}
    ("resto_sent", "ASIG"):      ["ASIG", "expr"],
    ("resto_sent", "MULT"):      ["term'", "expr'"],
    ("resto_sent", "DIV"):       ["term'", "expr'"],
    ("resto_sent", "MOD"):       ["term'", "expr'"],
    ("resto_sent", "PLUS"):      ["term'", "expr'"],
    ("resto_sent", "MINUS"):     ["term'", "expr'"],
    ("resto_sent", "SEMICOLON"): ["term'", "expr'"],

    ("expr",  "ID"):     ["term", "expr'"],
    ("expr",  "NUM"):    ["term", "expr'"],
    ("expr",  "MINUS"):  ["term", "expr'"],
    ("expr",  "ABS"):    ["term", "expr'"],
    ("expr",  "SIN"):    ["term", "expr'"],
    ("expr",  "COS"):    ["term", "expr'"],
    ("expr",  "TAN"):    ["term", "expr'"],
    ("expr",  "LPAREN"): ["term", "expr'"],

    ("expr'", "PLUS"):      ["PLUS",  "term", "expr'"],
    ("expr'", "MINUS"):     ["MINUS", "term", "expr'"],
    ("expr'", "SEMICOLON"): ["ε"],
    ("expr'", "RPAREN"):    ["ε"],
    ("expr'", "$"):         ["ε"],

    ("term",  "ID"):     ["factor", "term'"],
    ("term",  "NUM"):    ["factor", "term'"],
    ("term",  "MINUS"):  ["factor", "term'"],
    ("term",  "ABS"):    ["factor", "term'"],
    ("term",  "SIN"):    ["factor", "term'"],
    ("term",  "COS"):    ["factor", "term'"],
    ("term",  "TAN"):    ["factor", "term'"],
    ("term",  "LPAREN"): ["factor", "term'"],

    ("term'", "MULT"):      ["MULT", "factor", "term'"],
    ("term'", "DIV"):       ["DIV",  "factor", "term'"],
    ("term'", "MOD"):       ["MOD",  "factor", "term'"],
    ("term'", "PLUS"):      ["ε"],
    ("term'", "MINUS"):     ["ε"],
    ("term'", "SEMICOLON"): ["ε"],
    ("term'", "RPAREN"):    ["ε"],
    ("term'", "$"):         ["ε"],

    ("factor", "LPAREN"): ["LPAREN", "expr", "RPAREN"],
    ("factor", "MINUS"):  ["MINUS",  "factor"],
    ("factor", "ABS"):    ["ABS",    "LPAREN", "expr", "RPAREN"],
    ("factor", "SIN"):    ["SIN",    "LPAREN", "expr", "RPAREN"],
    ("factor", "COS"):    ["COS",    "LPAREN", "expr", "RPAREN"],
    ("factor", "TAN"):    ["TAN",    "LPAREN", "expr", "RPAREN"],
    ("factor", "NUM"):    ["NUM"],
    ("factor", "ID"):     ["ID"],
}


def print_sets():
    print("=" * 60)
    print("  CONJUNTOS FIRST")
    print("=" * 60)
    for nt, s in FIRST.items():
        tokens = ", ".join(sorted(s))
        print(f"  FIRST({nt:<14}) = {{ {tokens} }}")

    print()
    print("=" * 60)
    print("  CONJUNTOS FOLLOW")
    print("=" * 60)
    for nt, s in FOLLOW.items():
        tokens = ", ".join(sorted(s))
        print(f"  FOLLOW({nt:<14}) = {{ {tokens} }}")

    print()
    print("=" * 60)
    print("  CONJUNTOS DE PREDICCIÓN")
    print("=" * 60)
    for (nt, prod), s in PREDICT.items():
        tokens = ", ".join(sorted(s))
        print(f"  PREDICT({nt:<12} → {prod:<30}) = {{ {tokens} }}")

    print()
    print("=" * 60)
    print("  VERIFICACIÓN LL(1)")
    print("=" * 60)
    # Agrupar por no-terminal y verificar intersecciones vacías
    from collections import defaultdict
    grupos = defaultdict(list)
    for (nt, prod), s in PREDICT.items():
        grupos[nt].append((prod, s))

    ok = True
    for nt, reglas in grupos.items():
        for i in range(len(reglas)):
            for j in range(i + 1, len(reglas)):
                inter = reglas[i][1] & reglas[j][1]
                if inter:
                    print(f"  CONFLICTO en '{nt}': "
                          f"'{reglas[i][0]}' y '{reglas[j][0]}' "
                          f"comparten {inter}")
                    ok = False
    if ok:
        print("La gramática ES LL(1)")
