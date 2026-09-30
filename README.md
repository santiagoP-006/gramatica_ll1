# Gramática LL(1) — Lenguaje de expresiones matemáticas

Compilador escrito en **Python puro**, sin ANTLR ni librerías externas. Implementa un lenguaje con:

- Operadores `+ - * / %` y menos unario
- Funciones `abs`, `sin`, `cos`, `tan` (también `Sin`, `Cos`, `Tan`), con ángulos en **grados**
- Asignación de variables

Incluye las tres fases de análisis (léxica, sintáctica y semántica). Además, el programa **calcula** los conjuntos PRIMEROS, SIGUIENTES y PREDICCIÓN, verifica la condición LL(1) y funciona con cualquier gramática leída desde un archivo, como las de las diapositivas de clase.

**Autores:** Yslen Natalia Moreno Gutiérrez · Santiago Patiño Sarmiento
**Materia:** Lenguajes de Programación — Universidad Sergio Arboleda

---

## Estructura del proyecto

```
gramatica_ll1/
├── gramatica.py      # Gramática del lenguaje + algoritmos: PRIMEROS, SIGUIENTES, PREDICCIÓN,
│                     # verificación LL(1), tabla M, recursión izquierda, factorización y traza
├── lexer.py          # Análisis léxico (tokens)
├── parser.py         # Análisis sintáctico: descendente recursivo LL(1) + nodos del AST
├── semantica.py      # Análisis semántico: tabla de símbolos, validaciones y evaluación
├── ast_grafico.py    # Dibujo del AST: texto, ventana (tkinter) e imagen SVG
├── interactivo.py    # Modo interactivo (REPL)
├── main.py           # Coordinador: une todas las fases
├── programa.txt      # Programa de ejemplo
└── pruebas/          # Programas de prueba y gramáticas de las diapositivas
```

| Fase | Archivo | Qué hace |
|------|---------|----------|
| Léxica | `lexer.py` | Convierte el texto en tokens y detecta caracteres inválidos |
| Sintáctica | `parser.py` | Verifica la estructura con un analizador descendente recursivo y construye el AST |
| Semántica | `semantica.py` | Valida variables, división y módulo por cero, `tan` indefinida, y evalúa |

---

## Gramática LL(1)

```
programa    → sentencia programa | ε
sentencia   → ID resto_sent ;
            | NUM term' expr' ;
            | - factor term' expr' ;
            | abs ( expr ) term' expr' ;
            | sin ( expr ) term' expr' ;
            | cos ( expr ) term' expr' ;
            | tan ( expr ) term' expr' ;
            | ( expr ) term' expr' ;
resto_sent  → = expr | term' expr'
expr        → term expr'
expr'       → + term expr' | - term expr' | ε
term        → factor term'
term'       → * factor term' | / factor term' | % factor term' | ε
factor      → ( expr ) | - factor | abs ( expr ) | sin ( expr )
            | cos ( expr ) | tan ( expr ) | NUM | ID
```

### Por qué es LL(1)

1. **Sin recursión izquierda:** `expr → expr + term` se reemplazó por `expr → term expr'`, y lo mismo se hizo con `term`.
2. **Factorizada:** la versión inicial `sentencia → ID = expr ; | expr ;` tenía un conflicto, porque ambas opciones pueden empezar con `ID`. Se factorizó con `resto_sent`: después de leer `ID`, el token `=` indica una asignación y cualquier otro token indica una expresión. Así el parser decide **con un solo token**.
3. **Conjuntos disjuntos:** el programa comprueba que los PRED de cada no terminal no se cruzan.

La asociatividad izquierda (`10 - 3 - 2 = 5`) se conserva porque las funciones `expr'` y `term'` reciben el valor acumulado de la izquierda.

---

## Conjuntos (calculados por el programa)

El programa no tiene los conjuntos escritos a mano: los **calcula** a partir de `GRAMMAR` con iteración de punto fijo.

### PRIMEROS

| No terminal | PRIMEROS |
|---|---|
| `programa` | ABS, COS, ID, LPAREN, MINUS, NUM, SIN, TAN, ε |
| `sentencia` | ABS, COS, ID, LPAREN, MINUS, NUM, SIN, TAN |
| `resto_sent` | ASIG, DIV, MINUS, MOD, MULT, PLUS, ε |
| `expr` | ABS, COS, ID, LPAREN, MINUS, NUM, SIN, TAN |
| `expr'` | MINUS, PLUS, ε |
| `term` | ABS, COS, ID, LPAREN, MINUS, NUM, SIN, TAN |
| `term'` | DIV, MOD, MULT, ε |
| `factor` | ABS, COS, ID, LPAREN, MINUS, NUM, SIN, TAN |

### SIGUIENTES

| No terminal | SIGUIENTES |
|---|---|
| `programa` | $ |
| `sentencia` | ABS, COS, ID, LPAREN, MINUS, NUM, SIN, TAN, $ |
| `resto_sent` | SEMICOLON |
| `expr` | RPAREN, SEMICOLON |
| `expr'` | RPAREN, SEMICOLON |
| `term` | MINUS, PLUS, RPAREN, SEMICOLON |
| `term'` | MINUS, PLUS, RPAREN, SEMICOLON |
| `factor` | DIV, MINUS, MOD, MULT, PLUS, RPAREN, SEMICOLON |

### PREDICCIÓN (decisiones principales)

| Producción | PRED |
|---|---|
| `programa → sentencia programa` | ABS, COS, ID, LPAREN, MINUS, NUM, SIN, TAN |
| `programa → ε` | $ |
| `resto_sent → = expr` | ASIG |
| `resto_sent → term' expr'` | DIV, MINUS, MOD, MULT, PLUS, SEMICOLON |
| `expr' → + term expr'` | PLUS |
| `expr' → - term expr'` | MINUS |
| `expr' → ε` | RPAREN, SEMICOLON |
| `term' → * factor term'` | MULT |
| `term' → / factor term'` | DIV |
| `term' → % factor term'` | MOD |
| `term' → ε` | MINUS, PLUS, RPAREN, SEMICOLON |

Cada opción de `sentencia` y de `factor` empieza con un token distinto, así que su PRED es ese mismo token.

**Resultado:** los PRED de cada no terminal son disjuntos → **la gramática ES LL(1)**.

---

## Requisitos

- Python 3.8 o superior
- Solo para la ventana del AST: `tkinter` (en Ubuntu: `sudo apt install python3-tk`)

---

## Uso

### Modo 1 — Compilar un programa

```bash
python3 main.py                       # usa programa.txt
python3 main.py pruebas/p1_valido.txt
```

Muestra, en orden: el código fuente, los conjuntos calculados, los tokens, el AST (en texto y como árbol dibujado), los resultados y la tabla de símbolos.

Opciones:

| Opción | Qué hace |
|---|---|
| `--traza` | Muestra la traza del análisis predictivo usando la tabla M |
| `--gui` | Abre una ventana con el AST dibujado |
| `--svg` | Guarda el AST en `arbol.svg` (se abre con el navegador) |

```bash
python3 main.py pruebas/p1_valido.txt --traza --gui
```

### Modo 2 — Analizar cualquier gramática

```bash
python3 main.py --gramatica archivo.txt ["cadena a analizar"]
```

El programa:
1. Lee la gramática del archivo.
2. Elimina la recursión izquierda inmediata.
3. Factoriza por la izquierda.
4. Calcula PRIMEROS, SIGUIENTES y PREDICCIÓN.
5. Verifica LL(1) y muestra los conflictos, si los hay.
6. Muestra la tabla M.
7. Si se da una cadena, muestra la traza y dice si es aceptada o rechazada.

Formato del archivo de gramática:

```
# comentario
S -> A fin
A -> x A | ε
```

El símbolo inicial es el de la primera regla. Los no terminales son los que aparecen a la izquierda de `->`, y los demás símbolos son terminales.

### Modo 3 — Interactivo

**Con el lenguaje:** escribes expresiones y ves el resultado al instante. Las variables se conservan entre líneas.

```bash
python3 main.py --interactivo
```

```
>>> x = 10
  x = 10
>>> y = x * 2 + Sin(30)
  y = 20.5
>>> 10 - 3 - 2
  = 5
>>> z + 1
  [SEMÁNTICO] Variable 'z' usada antes de ser declarada
```

| Comando | Qué hace |
|---|---|
| `:vars` | Muestra la tabla de símbolos |
| `:conjuntos` | Muestra PRIMEROS, SIGUIENTES y PREDICCIÓN |
| `:tokens` | Activa o desactiva la vista de tokens |
| `:arbol` | Activa o desactiva el AST dibujado en texto |
| `:grafico` | Activa o desactiva la ventana del AST |
| `:svg` | Guarda el AST de la última expresión en `arbol.svg` |
| `:traza` | Activa o desactiva la traza con la tabla M |
| `:borrar` | Elimina todas las variables |
| `:ayuda` | Muestra la ayuda |
| `:salir` | Termina |

**Con otra gramática:** escribes cadenas de tokens y ves si son aceptadas.

```bash
python3 main.py --interactivo --gramatica pruebas/g_diapo14.txt
```

Comandos: `:gramatica`, `:conjuntos`, `:tabla`, `:ayuda`, `:salir`.

Con otra gramática solo se puede verificar si una cadena pertenece al lenguaje. Los resultados numéricos existen únicamente para el lenguaje de expresiones, porque es el único que tiene parte semántica.

---

## Gráfico del AST

El AST se muestra de tres formas, sin librerías externas:

- **Texto** (siempre, en la fase sintáctica):
```
  programa
  └── =
      ├── y
      └── +
          ├── *
          │   ├── x
          │   └── 2
          └── sin
              └── 30
```
- **Ventana** con `--gui` o `:grafico`, dibujada con tkinter.
- **Imagen** con `--svg` o `:svg`, guardada en `arbol.svg`.

Colores: naranja para asignación, azul para operadores, morado para funciones, verde para números y amarillo para variables.

---

## Pruebas de implementación

### Programas del lenguaje

| Archivo | Tipo | Resultado esperado |
|---|---|---|
| `p1_valido.txt` | Caso válido | 10, 3, 16, 5, 1, 3.333333, 6, 2, −14 y `COMPILADO` |
| `p2_error_lexico.txt` | Léxico | `[LÉXICO] Carácter no reconocido '$' en línea 2` |
| `p3_error_sintactico.txt` | Sintáctico | `[SINTÁCTICO] Se esperaba 'RPAREN' pero se encontró 'SEMICOLON'` |
| `p4_division_cero.txt` | Semántico | `[SEMÁNTICO] División por cero` |
| `p5_variable_no_definida.txt` | Semántico | `[SEMÁNTICO] Variable 'x' usada antes de ser declarada` |
| `p6_tan_indefinida.txt` | Semántico | `[SEMÁNTICO] tan(90.0) no está definida` |

```bash
python3 main.py pruebas/p1_valido.txt
python3 main.py pruebas/p2_error_lexico.txt
python3 main.py pruebas/p3_error_sintactico.txt
python3 main.py pruebas/p4_division_cero.txt
python3 main.py pruebas/p5_variable_no_definida.txt
python3 main.py pruebas/p6_tan_indefinida.txt
```

### Gramáticas de las diapositivas

| Archivo | Gramática | Resultado |
|---|---|---|
| `g_diapo06.txt` | `A → B uno \| dos`, `B → dos` | **NO es LL(1)**: conflicto en `A` por `dos` |
| `g_diapo12.txt` | `I → if E then I endif \| if E then I else I endif` | Factoriza a `I → if E then I I'`, `I' → endif \| else I endif` |
| `g_diapo14.txt` | `A → B uno \| dos`, `B → tres \| cuatro A` | ES LL(1); `cuatro dos uno` es aceptada |
| `g_diapo18.txt` | `S → A fin`, `A → x A \| ε` | ES LL(1); PRIMERO(A) = {x, ε}, SIGUIENTE(A) = {fin} |
| `g_diapo19.txt` | `S → S uno \| A`, `A → dos A \| tres` | Elimina la recursión: `S → A S'`, `S' → uno S' \| ε`; `dos tres uno` es aceptada |
| `g_expresiones.txt` | `E → E + T \| T` … | Genera `E'` y `T'` automáticamente |

```bash
python3 main.py --gramatica pruebas/g_diapo06.txt
python3 main.py --gramatica pruebas/g_diapo12.txt
python3 main.py --gramatica pruebas/g_diapo14.txt "cuatro dos uno"
python3 main.py --gramatica pruebas/g_diapo18.txt "x x fin"
python3 main.py --gramatica pruebas/g_diapo19.txt "dos tres uno"
python3 main.py --gramatica pruebas/g_expresiones.txt "id + id * id"
```

Traza de `cuatro dos uno`, que coincide con la diapositiva 17:

```
Paso  Pila              Entrada              Acción
1     A $               cuatro dos uno $     A → B uno
2     B uno $           cuatro dos uno $     B → cuatro A
3     cuatro A uno $    cuatro dos uno $     consumir cuatro
4     A uno $           dos uno $            A → dos
5     dos uno $         dos uno $            consumir dos
6     uno $             uno $                consumir uno
7     $                 $                    aceptación
```
