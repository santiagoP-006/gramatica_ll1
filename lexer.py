# lexer.py
# Analizador léxico para el lenguaje de expresiones matemáticas
# Produce una lista de tokens (tipo, valor, línea) a partir del código fuente

import re

# Orden importa: palabras reservadas ANTES que ID
TOKEN_SPEC = [
    ("NUM",       r'\d+(\.\d+)?'),
    ("ABS",       r'\babs\b'),
    ("SIN",       r'\bsin\b'),
    ("COS",       r'\bcos\b'),
    ("TAN",       r'\btan\b'),
    ("ID",        r'[a-zA-Z_]\w*'),
    ("ASIG",      r'='),
    ("PLUS",      r'\+'),
    ("MINUS",     r'-'),
    ("MULT",      r'\*'),
    ("DIV",       r'/'),
    ("MOD",       r'%'),
    ("LPAREN",    r'\('),
    ("RPAREN",    r'\)'),
    ("SEMICOLON", r';'),
    ("NEWLINE",   r'\n'),
    ("SKIP",      r'[ \t]+'),
    ("MISMATCH",  r'.'),
]

MASTER_PATTERN = re.compile(
    '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_SPEC)
)

class LexerError(Exception):
    pass

class Token:
    def __init__(self, type_, value, line):
        self.type  = type_
        self.value = value
        self.line  = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, línea={self.line})"

def tokenize(source_code: str) -> list:
    tokens = []
    line_num = 1

    for mo in MASTER_PATTERN.finditer(source_code):
        kind  = mo.lastgroup
        value = mo.group()

        if kind == "NEWLINE":
            line_num += 1
        elif kind == "SKIP":
            pass
        elif kind == "MISMATCH":
            raise LexerError(
                f"[LÉXICO] Carácter no reconocido '{value}' en línea {line_num}"
            )
        else:
            tokens.append(Token(kind, value, line_num))

    tokens.append(Token("$", "$", line_num))  # Marca de fin de entrada
    return tokens
