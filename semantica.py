# semantica.py
# Analizador semántico y evaluador del AST
# Detecta: variables no declaradas, división por cero
# Evalúa: el resultado numérico de cada sentencia

import math
from parser import (
    NumNode, IdNode, BinOpNode, UnaryOpNode,
    FuncNode, AssignNode, ProgramNode
)

class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self):
        # Tabla de símbolos: nombre → valor numérico
        self.symbol_table: dict = {}

    def analyze(self, node):
        """Punto de entrada: recibe el nodo raíz del AST."""
        if isinstance(node, ProgramNode):
            return self._visit_program(node)
        raise SemanticError("[SEMÁNTICO] Nodo raíz no reconocido")

    def _visit_program(self, node: ProgramNode):
        results = []
        for stmt in node.statements:
            result = self._visit(stmt)
            results.append(result)
        return results

    def _visit(self, node):
        if isinstance(node, NumNode):
            return node.value

        elif isinstance(node, IdNode):
            if node.name not in self.symbol_table:
                raise SemanticError(
                    f"[SEMÁNTICO] Variable '{node.name}' usada antes de ser declarada"
                )
            return self.symbol_table[node.name]

        elif isinstance(node, AssignNode):
            value = self._visit(node.expr)
            self.symbol_table[node.name] = value
            return value

        elif isinstance(node, UnaryOpNode):
            val = self._visit(node.operand)
            if node.op == "-":
                return -val
            raise SemanticError(f"[SEMÁNTICO] Operador unario desconocido: {node.op}")

        elif isinstance(node, BinOpNode):
            left  = self._visit(node.left)
            right = self._visit(node.right)
            if node.op == "+": return left + right
            if node.op == "-": return left - right
            if node.op == "*": return left * right
            if node.op == "/":
                if right == 0:
                    raise SemanticError("[SEMÁNTICO] División por cero")
                return left / right
            if node.op == "%":
                if right == 0:
                    raise SemanticError("[SEMÁNTICO] Módulo por cero")
                return left % right
            raise SemanticError(f"[SEMÁNTICO] Operador binario desconocido: {node.op}")

        elif isinstance(node, FuncNode):
            arg = self._visit(node.arg)
            if node.func == "sin": return math.sin(math.radians(arg))
            if node.func == "cos": return math.cos(math.radians(arg))
            if node.func == "tan":
                if abs(math.cos(math.radians(arg))) < 1e-10:
                    raise SemanticError(
                        f"[SEMÁNTICO] tan({arg}) no está definida (cos ≈ 0)"
                    )
                return math.tan(math.radians(arg))
            if node.func == "abs": return abs(arg)
            raise SemanticError(f"[SEMÁNTICO] Función no reconocida: {node.func}")

        else:
            raise SemanticError(f"[SEMÁNTICO] Nodo AST no reconocido: {type(node)}")

    def print_symbol_table(self):
        if not self.symbol_table:
            print("  (tabla de símbolos vacía)")
            return
        print(f"  {'Variable':<15} {'Valor':>15}")
        print(f"  {'-'*30}")
        for name, val in self.symbol_table.items():
            print(f"  {name:<15} {val:>15.6f}")
