# parser.py
# Analizador sintáctico LL(1) ESTRICTO — un solo token de anticipación
# Corrección: parse_sentencia usa resto_sent en lugar de peek_next()

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

# ── Parser LL(1) estricto ─────────────────────────────────────
class Parser:
    def __init__(self, tokens: list):
        self.tokens = tokens
        self.pos    = 0

    def current(self) -> Token:
        return self.tokens[self.pos]

    # peek_next() eliminado — ya no se usa
    def consume(self, expected_type: str) -> Token:
        tok = self.current()
        if tok.type != expected_type:
            raise ParseError(
                f"[SINTÁCTICO] Se esperaba '{expected_type}' "
                f"pero se encontró '{tok.type}' ('{tok.value}') "
                f"en línea {tok.line}"
            )
        self.pos += 1
        return tok

    # programa → sentencia programa | ε
    def parse_programa(self) -> ProgramNode:
        stmts = []
        start = {"ID", "NUM", "MINUS", "ABS", "SIN", "COS", "TAN","ATAN", "LPAREN"}
        while self.current().type in start:
            stmts.append(self.parse_sentencia())
        return ProgramNode(stmts)

    # sentencia → ID resto_sent ;
    #           | NUM    term' expr' ;
    #           | MINUS  factor term' expr' ;
    #           | ABS  ( expr ) term' expr' ;
    #           | SIN  ( expr ) term' expr' ;
    #           | COS  ( expr ) term' expr' ;
    #           | TAN  ( expr ) term' expr' ;
    #           | ( expr ) term' expr' ;
    def parse_sentencia(self):
        tok = self.current()

        if tok.type == "ID":
            name = self.consume("ID").value
            # resto_sent: un solo token decide — ASIG o cualquier otra cosa
            node = self.parse_resto_sent(name)
            self.consume("SEMICOLON")
            return node

        elif tok.type == "NUM":
            left = NumNode(self.consume("NUM").value)
            left = self.parse_term_prime(left)
            node = self.parse_expr_prime(left)
            self.consume("SEMICOLON")
            return node

        elif tok.type == "MINUS":
            self.consume("MINUS")
            operand = self.parse_factor()
            left    = UnaryOpNode("-", operand)
            left    = self.parse_term_prime(left)
            node    = self.parse_expr_prime(left)
            self.consume("SEMICOLON")
            return node

        elif tok.type in ("ABS", "SIN", "COS", "TAN", "ATAN"):
            func = self.consume(tok.type).value
            self.consume("LPAREN")
            arg  = self.parse_expr()
            self.consume("RPAREN")
            left = FuncNode(func, arg)
            left = self.parse_term_prime(left)
            node = self.parse_expr_prime(left)
            self.consume("SEMICOLON")
            return node

        elif tok.type == "LPAREN":
            self.consume("LPAREN")
            inner = self.parse_expr()
            self.consume("RPAREN")
            left  = self.parse_term_prime(inner)
            node  = self.parse_expr_prime(left)
            self.consume("SEMICOLON")
            return node

        else:
            raise ParseError(
                f"[SINTÁCTICO] Inicio de sentencia inválido: "
                f"'{tok.type}' ('{tok.value}') en línea {tok.line}"
            )

    # resto_sent → ASIG expr          (asignación)
    #            | term' expr'         (expresión que empezó con ID)
    # Decisión con UN solo token: si es ASIG → asignación, si no → expresión
    def parse_resto_sent(self, id_name: str):
        if self.current().type == "ASIG":
            # M[resto_sent, ASIG] → ASIG expr
            self.consume("ASIG")
            expr = self.parse_expr()
            return AssignNode(id_name, expr)
        else:
            # M[resto_sent, {MULT,DIV,MOD,PLUS,MINUS,SEMICOLON}] → term' expr'
            # El ID ya fue consumido; lo envolvemos como IdNode y continuamos
            left = self.parse_term_prime(IdNode(id_name))
            return self.parse_expr_prime(left)

    # expr → term expr'
    def parse_expr(self):
        node = self.parse_term()
        return self.parse_expr_prime(node)

    # expr' → + term expr' | - term expr' | ε
    def parse_expr_prime(self, left):
        if self.current().type == "PLUS":
            self.consume("PLUS")
            right = self.parse_term()
            return self.parse_expr_prime(BinOpNode("+", left, right))
        elif self.current().type == "MINUS":
            self.consume("MINUS")
            right = self.parse_term()
            return self.parse_expr_prime(BinOpNode("-", left, right))
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
            return self.parse_term_prime(BinOpNode("*", left, right))
        elif self.current().type == "DIV":
            self.consume("DIV")
            right = self.parse_factor()
            return self.parse_term_prime(BinOpNode("/", left, right))
        elif self.current().type == "MOD":
            self.consume("MOD")
            right = self.parse_factor()
            return self.parse_term_prime(BinOpNode("%", left, right))
        return left  # ε

    # factor → ( expr ) | - factor | abs(expr) | sin(expr)
    #        | cos(expr) | tan(expr) | NUM | ID
    def parse_factor(self):
        tok = self.current()

        if tok.type == "LPAREN":
            self.consume("LPAREN")
            node = self.parse_expr()
            self.consume("RPAREN")
            return node

        elif tok.type == "MINUS":
            self.consume("MINUS")
            return UnaryOpNode("-", self.parse_factor())

        elif tok.type in ("ABS", "SIN", "COS", "TAN","ATAN"):
            func = self.consume(tok.type).value
            self.consume("LPAREN")
            arg  = self.parse_expr()
            self.consume("RPAREN")
            return FuncNode(func, arg)

        elif tok.type == "NUM":
            return NumNode(self.consume("NUM").value)

        elif tok.type == "ID":
            return IdNode(self.consume("ID").value)

        else:
            raise ParseError(
                f"[SINTÁCTICO] Token inesperado en factor: "
                f"'{tok.type}' ('{tok.value}') en línea {tok.line}"
            )

    def parse(self) -> ProgramNode:
        tree = self.parse_programa()
        self.consume("$")
        return tree
