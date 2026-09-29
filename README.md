# Gramática LL(1) — Expresiones Matemáticas con Variables

---

## Descripción

Este proyecto implementa las tres fases más importante de un compilador para un lenguaje diseñado desde cero:

| Fase | Archivo | Responsabilidad |
|------|---------|-----------------|
| Léxico | `lexer.py` | Convierte el código fuente en tokens |
| Sintáctico | `parser.py` | Valida la estructura gramatical y construye el AST |
| Semántico | `semantic.py` | Valida variables, evalúa expresiones y gestiona la tabla de símbolos |

La gramática fue diseñada formalmente como **LL(1)**: sin ambigüedad, sin recursión por la izquierda y sin factores comunes, lo que permite un análisis determinista con un solo token de anticipación.

---

## Estructura del proyecto

```
gramatica_ll1/
├── grammar.py      # Gramática formal + conjuntos FIRST, FOLLOW y tabla de predicción
├── lexer.py        # Analizador léxico (tokenizador)
├── parser.py       # Parser LL(1) descendente recursivo + nodos del AST
├── semantic.py     # Analizador semántico + evaluador numérico
├── programa.txt    # Código fuente de prueba
└── main.py         # Coordinador principal (entrada del sistema)
```

---

## Lenguaje soportado

### Operadores

| Operador | Símbolo | Ejemplo |
|----------|---------|---------|
| Suma | `+` | `x + 2` |
| Resta | `-` | `x - 1` |
| Multiplicación | `*` | `x * 3` |
| División | `/` | `x / 4` |
| Módulo | `%` | `x % 2` |
| Valor absoluto | `abs(...)` | `abs(-5)` |

### Funciones trigonométricas

| Función | Ejemplo |
|---------|---------|
| Seno | `sin(90)` |
| Coseno | `cos(0)` |
| Tangente | `tan(45)` |

### Asignación de variables

```
x = 10;
y = x + sin(30);
```

---

## Gramática formal

```
programa  → sentencia programa | ε
sentencia → ID = expr ; | expr ;
expr      → term expr'
expr'     → + term expr' | - term expr' | ε
term      → factor term'
term'     → * factor term' | / factor term' | % factor term' | ε
factor    → ( expr )
          | - factor
          | abs ( expr )
          | sin ( expr )
          | cos ( expr )
          | tan ( expr )
          | NUM
          | ID
```

---

## Conjuntos formales

### FIRST

| No-terminal | FIRST |
|-------------|-------|
| `programa` | ID, NUM, MINUS, ABS, SIN, COS, TAN, LPAREN, ε |
| `sentencia` | ID, NUM, MINUS, ABS, SIN, COS, TAN, LPAREN |
| `expr` | ID, NUM, MINUS, ABS, SIN, COS, TAN, LPAREN |
| `expr'` | PLUS, MINUS, ε |
| `term` | ID, NUM, MINUS, ABS, SIN, COS, TAN, LPAREN |
| `term'` | MULT, DIV, MOD, ε |
| `factor` | LPAREN, MINUS, ABS, SIN, COS, TAN, NUM, ID |

### FOLLOW

| No-terminal | FOLLOW |
|-------------|--------|
| `programa` | $ |
| `sentencia` | ID, NUM, MINUS, ABS, SIN, COS, TAN, LPAREN, $ |
| `expr` | SEMICOLON, RPAREN, $ |
| `expr'` | SEMICOLON, RPAREN, $ |
| `term` | PLUS, MINUS, SEMICOLON, RPAREN, $ |
| `term'` | PLUS, MINUS, SEMICOLON, RPAREN, $ |
| `factor` | MULT, DIV, MOD, PLUS, MINUS, SEMICOLON, RPAREN, $ |

> **Verificación LL(1):** ningún par de producciones del mismo no-terminal comparte elementos en sus conjuntos de predicción → la gramática **es LL(1)** ✓

### Tabla de predicción (fragmento)

| M[No-terminal, Token] | Producción |
|-----------------------|-----------|
| M[expr', PLUS] | expr' → + term expr' |
| M[expr', MINUS] | expr' → - term expr' |
| M[expr', SEMICOLON] | expr' → ε |
| M[term', MULT] | term' → * factor term' |
| M[term', DIV] | term' → / factor term' |
| M[term', MOD] | term' → % factor term' |
| M[term', PLUS] | term' → ε |
| M[factor, SIN] | factor → sin ( expr ) |
| M[factor, COS] | factor → cos ( expr ) |
| M[factor, TAN] | factor → tan ( expr ) |
| M[factor, ABS] | factor → abs ( expr ) |
| M[factor, NUM] | factor → NUM |
| M[factor, ID] | factor → ID |

---

## Requisitos

- Python 3.6 o superior
- Sin dependencias externas (solo biblioteca estándar de Python)

---

## Uso

### Ejecución con el archivo de prueba por defecto

```bash
python3 main.py
```

### Ejecución con un archivo fuente personalizado

```bash
python3 main.py mi_programa.txt
```

### Ver solo los conjuntos formales

```bash
python3 -c "from grammar import print_sets; print_sets()"
```

---

## Ejemplo de entrada (`programa.txt`)

```
x = 10;
y = 3;
z = x + y * 2;
resultado = abs(-5) + sin(90);
angulo = cos(0) + tan(45);
r = (x - y) % 4;
w = x / y;
sin(30) + cos(60);
abs(-100) * 2;
```

### Salida esperada (fragmento)

```
============================================================
  GRAMÁTICA LL(1) — EXPRESIONES MATEMÁTICAS CON VARIABLES
============================================================
  Archivo fuente: programa.txt

============================================================
  FASE 1 — ANÁLISIS LÉXICO
============================================================
  Token(ID, 'x', línea=1)
  Token(ASIG, '=', línea=1)
  Token(NUM, '10', línea=1)
  ...

============================================================
  FASE 3 — ANÁLISIS SEMÁNTICO Y EVALUACIÓN
============================================================
  Sentencia 1: Assign(x, Num(10.0))
    → Resultado: 10.000000

  Sentencia 3: Assign(z, BinOp(+, Id(x), BinOp(*, Id(y), Num(2.0))))
    → Resultado: 16.000000

============================================================
  TABLA DE SÍMBOLOS (Variables declaradas)
============================================================
  Variable          Valor
  ------------------------------
  x               10.000000
  y                3.000000
  z               16.000000
  resultado        6.000000
  angulo           2.000000
  r                3.000000
  w                3.333333

============================================================
  COMPILACIÓN EXITOSA ✓
============================================================
```

---

## Detección de errores

El compilador detecta y reporta errores en las tres fases con mensajes claros:

### Error léxico — carácter no reconocido

```
[LÉXICO] Carácter no reconocido '@' en línea 1
```

### Error sintáctico — estructura inválida

```
[SINTÁCTICO] Se esperaba 'RPAREN' pero se encontró 'SEMICOLON' (';') en línea 1
```

### Error semántico — variable no declarada

```
[SEMÁNTICO] Variable 'w' usada antes de ser declarada
```

### Error semántico — división por cero

```
[SEMÁNTICO] División por cero
```

---

## Pruebas de implementación

| # | Comando | Tipo de prueba | Resultado esperado |
|---|---------|----------------|--------------------|
| 1 | `python3 main.py programa.txt` | Caso válido completo | Compilación exitosa, resultados numéricos y tabla de símbolos |
| 2 | `echo "x = 10@5;" \| python3 ...` | Error léxico | Mensaje con carácter inválido y línea |
| 3 | `echo "x = (10 + 5;" > f.txt && python3 main.py f.txt` | Error sintáctico | Mensaje con token esperado vs encontrado |
| 4 | `echo "z = w + 5;" > f.txt && python3 main.py f.txt` | Error semántico | Mensaje de variable no declarada |
| 5 | `echo "r = 10 / 0;" > f.txt && python3 main.py f.txt` | Error semántico | Mensaje de división por cero |
| 6 | `python3 -c "from grammar import print_sets; print_sets()"` | Conjuntos formales | FIRST, FOLLOW y tabla de predicción completos |

---


