# gramatica.py
# Contiene: produccciones, conjuntos FIRST, FOLLOW y tabla de predicción

GRAMMAR = {
    "programa": [
        ["sentencia", "programa"],
        ["ε"]
    ],
    "sentencia": [
        ["ID", "ASIG", "expr", "SEMICOLON"],
        ["expr", "SEMICOLON"]
    ],
    "expr": [
        ["term", "expr'"]
    ],
    "expr'": [
        ["PLUS", "term", "expr'"],
        ["MINUS", "term", "expr'"],
        ["ε"]
    ],
    "term": [
        ["factor", "term'"]
    ],
    "term'": [
        ["MULT", "factor", "term'"],
        ["DIV", "factor", "term'"],
        ["MOD", "factor", "term'"],
        ["ε"]
    ],
    "factor": [
        ["LPAREN", "expr", "RPAREN"],
        ["MINUS", "factor"],
        ["ABS", "LPAREN", "expr", "RPAREN"],
        ["SIN", "LPAREN", "expr", "RPAREN"],
        ["COS", "LPAREN", "expr", "RPAREN"],
        ["TAN", "LPAREN", "expr", "RPAREN"],
        ["NUM"],
        ["ID"]
    ]
}

FIRST = {
    "programa":  {"ID", "NUM", "MINUS", "ABS", "SIN", "COS", "TAN", "LPAREN", "ε"},
    "sentencia": {"ID", "NUM", "MINUS", "ABS", "SIN", "COS", "TAN", "LPAREN"},
    "expr":      {"ID", "NUM", "MINUS", "ABS", "SIN", "COS", "TAN", "LPAREN"},
    "expr'":     {"PLUS", "MINUS", "ε"},
    "term":      {"ID", "NUM", "MINUS", "ABS", "SIN", "COS", "TAN", "LPAREN"},
    "term'":     {"MULT", "DIV", "MOD", "ε"},
    "factor":    {"LPAREN", "MINUS", "ABS", "SIN", "COS", "TAN", "NUM", "ID"}
}

FOLLOW = {
    "programa":  {"$"},
    "sentencia": {"ID", "NUM", "MINUS", "ABS", "SIN", "COS", "TAN", "LPAREN", "$"},
    "expr":      {"SEMICOLON", "RPAREN", "$"},
    "expr'":     {"SEMICOLON", "RPAREN", "$"},
    "term":      {"PLUS", "MINUS", "SEMICOLON", "RPAREN", "$"},
    "term'":     {"PLUS", "MINUS", "SEMICOLON", "RPAREN", "$"},
    "factor":    {"MULT", "DIV", "MOD", "PLUS", "MINUS", "SEMICOLON", "RPAREN", "$"}
}

# Tabla de predicción: (no_terminal, token) → producción
PARSING_TABLE = {
    ("programa",  "ID"):       ["sentencia", "programa"],
    ("programa",  "NUM"):      ["sentencia", "programa"],
    ("programa",  "MINUS"):    ["sentencia", "programa"],
    ("programa",  "ABS"):      ["sentencia", "programa"],
    ("programa",  "SIN"):      ["sentencia", "programa"],
    ("programa",  "COS"):      ["sentencia", "programa"],
    ("programa",  "TAN"):      ["sentencia", "programa"],
    ("programa",  "LPAREN"):   ["sentencia", "programa"],
    ("programa",  "$"):        ["ε"],

    # sentencia se resuelve en el parser con lookahead doble
    ("sentencia", "ID"):       ["ID", "ASIG", "expr", "SEMICOLON"],
    ("sentencia", "NUM"):      ["expr", "SEMICOLON"],
    ("sentencia", "MINUS"):    ["expr", "SEMICOLON"],
    ("sentencia", "ABS"):      ["expr", "SEMICOLON"],
    ("sentencia", "SIN"):      ["expr", "SEMICOLON"],
    ("sentencia", "COS"):      ["expr", "SEMICOLON"],
    ("sentencia", "TAN"):      ["expr", "SEMICOLON"],
    ("sentencia", "LPAREN"):   ["expr", "SEMICOLON"],

    ("expr",  "ID"):    ["term", "expr'"],
    ("expr",  "NUM"):   ["term", "expr'"],
    ("expr",  "MINUS"): ["term", "expr'"],
    ("expr",  "ABS"):   ["term", "expr'"],
    ("expr",  "SIN"):   ["term", "expr'"],
    ("expr",  "COS"):   ["term", "expr'"],
    ("expr",  "TAN"):   ["term", "expr'"],
    ("expr",  "LPAREN"):["term", "expr'"],

    ("expr'", "PLUS"):       ["PLUS", "term", "expr'"],
    ("expr'", "MINUS"):      ["MINUS", "term", "expr'"],
    ("expr'", "SEMICOLON"):  ["ε"],
    ("expr'", "RPAREN"):     ["ε"],
    ("expr'", "$"):          ["ε"],

    ("term",  "ID"):    ["factor", "term'"],
    ("term",  "NUM"):   ["factor", "term'"],
    ("term",  "MINUS"): ["factor", "term'"],
    ("term",  "ABS"):   ["factor", "term'"],
    ("term",  "SIN"):   ["factor", "term'"],
    ("term",  "COS"):   ["factor", "term'"],
    ("term",  "TAN"):   ["factor", "term'"],
    ("term",  "LPAREN"):["factor", "term'"],

    ("term'", "MULT"):      ["MULT", "factor", "term'"],
    ("term'", "DIV"):       ["DIV",  "factor", "term'"],
    ("term'", "MOD"):       ["MOD",  "factor", "term'"],
    ("term'", "PLUS"):      ["ε"],
    ("term'", "MINUS"):     ["ε"],
    ("term'", "SEMICOLON"): ["ε"],
    ("term'", "RPAREN"):    ["ε"],
    ("term'", "$"):         ["ε"],

    ("factor", "LPAREN"): ["LPAREN", "expr", "RPAREN"],
    ("factor", "MINUS"):  ["MINUS", "factor"],
    ("factor", "ABS"):    ["ABS",   "LPAREN", "expr", "RPAREN"],
    ("factor", "SIN"):    ["SIN",   "LPAREN", "expr", "RPAREN"],
    ("factor", "COS"):    ["COS",   "LPAREN", "expr", "RPAREN"],
    ("factor", "TAN"):    ["TAN",   "LPAREN", "expr", "RPAREN"],
    ("factor", "NUM"):    ["NUM"],
    ("factor", "ID"):     ["ID"],
}

def print_sets():
    print("=" * 60)
    print("  CONJUNTOS FIRST")
    print("=" * 60)
    for nt, s in FIRST.items():
        tokens = ", ".join(sorted(s))
        print(f"  FIRST({nt:<12}) = {{ {tokens} }}")

    print()
    print("=" * 60)
    print("  CONJUNTOS FOLLOW")
    print("=" * 60)
    for nt, s in FOLLOW.items():
        tokens = ", ".join(sorted(s))
        print(f"  FOLLOW({nt:<12}) = {{ {tokens} }}")

    print()
    print("=" * 60)
    print("  TABLA DE PREDICCIÓN (fragmento relevante)")
    print("=" * 60)
    for (nt, tok), prod in PARSING_TABLE.items():
        print(f"  M[{nt:<12}, {tok:<12}] → {' '.join(prod)}")
