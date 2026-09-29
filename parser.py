# parser.py
# Analizador sintáctico LL(1) descendente recursivo
# Construye el AST a partir de la lista de tokens del lexer

from lexer import Token, LexerError

class ParseError(Exception):
    pass

# ── Nodos del AST ─────────────────────────────────────────────
class NumNode:
    def __init__(self, value):
        self.value = float(value)
    def __repr__(self): return f"Num({self.value})"

class IdNode:
    def __init__(self, name):
        self.name = name
    def __repr__(self): return f"Id({self.name})"

class BinOpNode:
    def __init__(self, op, left, right):
        self.op, self.left, self.right = op, left, right
    def __repr__(self): return f"BinOp({self.op}, {self.left}, {self.right})"

class UnaryOpNode:
    def __init__(self, op, operand):
        self.op, self.operand = op, operand
    def __repr__(self): return f"UnaryOp({self.op}, {self.operand})"

class FuncNode:
    def __init__(self, func, arg):
        self.func, self.arg = func, arg
    def __repr__(self): return f"Func({self.func}, {self.arg})"

class AssignNode:
    def __init__(self, name, expr):
        self.name, self.expr = name, expr
    def __repr__(self): return f"Assign({self.name}, {self.expr})"

class ProgramNode:
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self): return f"Program({self.statements})"

# ── Parser ────────────────────────────────────────────────────
class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos    = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek_next(self) -> Token:
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return Token("$", "$", -1)

    def consume(self, expected_type: str) -> Token:
        tok = self.current()
        if tok.type != expected_type:
            raise ParseError(
                f"[SINTÁCTICO] Se esperaba '{expected_type}' "
                f"pero se encontró '{tok.type}' ('{tok.value}') en línea {tok.line}"
            )
        self.pos += 1
        return tok

    # programa → sentencia programa | ε
    def parse_programa(self) -> ProgramNode:
        stmts = []
        start_types = {"ID", "NUM", "MINUS", "ABS", "SIN", "COS", "TAN", "LPAREN"}
        while self.current().type in start_types:
            stmts.append(self.parse_sentencia())
        return ProgramNode(stmts)

    # sentencia → ID = expr ; | expr ;
    def parse_sentencia(self):
        if self.current().type == "ID" and self.peek_next().type == "ASIG":
            name = self.consume("ID").value
            self.consume("ASIG")
            expr = self.parse_expr()
            self.consume("SEMICOLON")
            return AssignNode(name, expr)
        else:
            expr = self.parse_expr()
            self.consume("SEMICOLON")
            return expr

    # expr → term expr'
    def parse_expr(self):
        node = self.parse_term()
        return self.parse_expr_prime(node)

    # expr' → + term expr' | - term expr' | ε
    def parse_expr_prime(self, left):
        if self.current().type == "PLUS":
            self.consume("PLUS")
            right = self.parse_term()
            node  = BinOpNode("+", left, right)
            return self.parse_expr_prime(node)
        elif self.current().type == "MINUS":
            self.consume("MINUS")
            right = self.parse_term()
            node  = BinOpNode("-", left, right)
            return self.parse_expr_prime(node)
        return left  # ε

    # term → factor term'
    def parse_term(self):
        node = self.parse_factor()
        return self.parse_term_prime(node)

    # term' → * factor term' | / factor term' | % factor term' | ε
    def parse_term_prime(self, left):
        if self.current().type == "MULT":
            self.consume("MULT")
            right = self.parse_factor()
            node  = BinOpNode("*", left, right)
            return self.parse_term_prime(node)
        elif self.current().type == "DIV":
            self.consume("DIV")
            right = self.parse_factor()
            node  = BinOpNode("/", left, right)
            return self.parse_term_prime(node)
        elif self.current().type == "MOD":
            self.consume("MOD")
            right = self.parse_factor()
            node  = BinOpNode("%", left, right)
            return self.parse_term_prime(node)
        return left  # ε

    # factor → ( expr ) | - factor | abs(expr) | sin(expr) | cos(expr) | tan(expr) | NUM | ID
    def parse_factor(self):
        tok = self.current()

        if tok.type == "LPAREN":
            self.consume("LPAREN")
            node = self.parse_expr()
            self.consume("RPAREN")
            return node

        elif tok.type == "MINUS":
            self.consume("MINUS")
            operand = self.parse_factor()
            return UnaryOpNode("-", operand)

        elif tok.type in ("ABS", "SIN", "COS", "TAN"):
            func = self.consume(tok.type).value
            self.consume("LPAREN")
            arg  = self.parse_expr()
            self.consume("RPAREN")
            return FuncNode(func, arg)

        elif tok.type == "NUM":
            self.consume("NUM")
            return NumNode(tok.value)

        elif tok.type == "ID":
            self.consume("ID")
            return IdNode(tok.value)

        else:
            raise ParseError(
                f"[SINTÁCTICO] Token inesperado '{tok.type}' ('{tok.value}') "
                f"en línea {tok.line}"
            )

    def parse(self) -> ProgramNode:
        tree = self.parse_programa()
        self.consume("$")
        return tree
