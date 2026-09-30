# ast_grafico.py
# Dibuja el AST de tres formas, sin librerías externas:
#   1. arbol_texto(ast)          → árbol en la terminal con ├── └──
#   2. guardar_svg(ast, ruta)    → imagen .svg (se abre con el navegador)
#   3. mostrar_ventana(ast)      → ventana gráfica con tkinter

from parser import (NumNode, IdNode, BinOpNode, UnaryOpNode,
                    FuncNode, AssignNode, ProgramNode)

# Colores por tipo de nodo: (relleno, borde)
COLORES = {
    "programa":   ("#e8e8e8", "#555555"),
    "asignacion": ("#ffe0b2", "#e65100"),
    "operador":   ("#bbdefb", "#0d47a1"),
    "funcion":    ("#e1bee7", "#4a148c"),
    "numero":     ("#c8e6c9", "#1b5e20"),
    "variable":   ("#fff9c4", "#f57f17"),
}


class Hoja:
    """Nodo auxiliar para mostrar el nombre de la variable asignada."""
    def __init__(self, nombre):
        self.nombre = nombre


def info(nodo):
    """Devuelve (etiqueta, tipo, hijos) de un nodo del AST."""
    if isinstance(nodo, ProgramNode):
        return "programa", "programa", nodo.statements
    if isinstance(nodo, AssignNode):
        return "=", "asignacion", [Hoja(nodo.name), nodo.expr]
    if isinstance(nodo, Hoja):
        return nodo.nombre, "variable", []
    if isinstance(nodo, BinOpNode):
        return nodo.op, "operador", [nodo.left, nodo.right]
    if isinstance(nodo, UnaryOpNode):
        return f"{nodo.op} (unario)", "operador", [nodo.operand]
    if isinstance(nodo, FuncNode):
        return nodo.func, "funcion", [nodo.arg]
    if isinstance(nodo, NumNode):
        v = nodo.value
        return (str(int(v)) if v == int(v) else str(v)), "numero", []
    if isinstance(nodo, IdNode):
        return nodo.name, "variable", []
    return type(nodo).__name__, "programa", []


# ── 1. Árbol en texto ─────────────────────────────────────────
def arbol_texto(nodo, prefijo="", ultimo=True, raiz=True):
    etiqueta, _, hijos = info(nodo)
    if raiz:
        lineas = [etiqueta]
        nuevo_prefijo = ""
    else:
        lineas = [prefijo + ("└── " if ultimo else "├── ") + etiqueta]
        nuevo_prefijo = prefijo + ("    " if ultimo else "│   ")
    for i, h in enumerate(hijos):
        lineas += arbol_texto(h, nuevo_prefijo, i == len(hijos) - 1, False).split("\n")
    return "\n".join(lineas)


# ── Posiciones para el dibujo ─────────────────────────────────
DX, DY = 70, 75          # separación horizontal y vertical
MARGEN = 40


def calcular_posiciones(raiz):
    """Hojas de izquierda a derecha; cada padre queda centrado sobre sus hijos."""
    nodos = []           # (x, y, etiqueta, tipo, indice_padre)
    siguiente_x = [0]

    def visitar(nodo, nivel, padre):
        etiqueta, tipo, hijos = info(nodo)
        indice = len(nodos)
        nodos.append([0, nivel, etiqueta, tipo, padre])
        if not hijos:
            ancho = max(1, len(etiqueta) / 5)       # etiquetas largas ocupan más
            nodos[indice][0] = siguiente_x[0] + ancho / 2
            siguiente_x[0] += ancho
        else:
            xs = [visitar(h, nivel + 1, indice) for h in hijos]
            nodos[indice][0] = (xs[0] + xs[-1]) / 2
        return nodos[indice][0]

    visitar(raiz, 0, None)
    pos = []
    for x, nivel, etiqueta, tipo, padre in nodos:
        pos.append((MARGEN + x * DX + DX / 2, MARGEN + nivel * DY + 20, etiqueta, tipo, padre))
    ancho = MARGEN * 2 + siguiente_x[0] * DX + DX
    alto = MARGEN * 2 + (max(n[1] for n in nodos) + 1) * DY
    return pos, ancho, alto


def medida(etiqueta):
    return max(36, 9 * len(etiqueta) + 16)      # ancho del óvalo


# ── 2. Imagen SVG ─────────────────────────────────────────────
def guardar_svg(nodo, ruta):
    pos, ancho, alto = calcular_posiciones(nodo)
    partes = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho:.0f}" '
              f'height="{alto:.0f}" font-family="monospace" font-size="14">',
              f'<rect width="100%" height="100%" fill="white"/>']
    for x, y, _, _, padre in pos:                       # primero las líneas
        if padre is not None:
            px, py = pos[padre][0], pos[padre][1]
            partes.append(f'<line x1="{px:.1f}" y1="{py:.1f}" x2="{x:.1f}" '
                          f'y2="{y:.1f}" stroke="#777" stroke-width="1.5"/>')
    for x, y, etiqueta, tipo, _ in pos:                 # luego los nodos
        relleno, borde = COLORES[tipo]
        texto = (etiqueta.replace("&", "&amp;").replace("<", "&lt;")
                 .replace(">", "&gt;"))
        partes.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{medida(etiqueta)/2:.1f}" '
                      f'ry="16" fill="{relleno}" stroke="{borde}" stroke-width="1.5"/>')
        partes.append(f'<text x="{x:.1f}" y="{y + 5:.1f}" text-anchor="middle">{texto}</text>')
    partes.append("</svg>")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(partes))


# ── 3. Ventana con tkinter ────────────────────────────────────
def mostrar_ventana(nodo, titulo="Árbol de sintaxis abstracta (AST)"):
    try:
        import tkinter as tk
    except ImportError:
        print("  [AVISO] tkinter no está instalado. En Ubuntu:  sudo apt install python3-tk")
        print("          Usa --svg para guardar el árbol como imagen.")
        return False

    pos, ancho, alto = calcular_posiciones(nodo)
    try:
        ventana = tk.Tk()
    except tk.TclError:
        print("  [AVISO] No hay pantalla disponible para abrir la ventana.")
        return False
    ventana.title(titulo)

    marco = tk.Frame(ventana)
    marco.pack(fill="both", expand=True)
    canvas = tk.Canvas(marco, bg="white", width=min(ancho, 1200), height=min(alto, 700),
                       scrollregion=(0, 0, ancho, alto))
    barra_x = tk.Scrollbar(marco, orient="horizontal", command=canvas.xview)
    barra_y = tk.Scrollbar(marco, orient="vertical", command=canvas.yview)
    canvas.configure(xscrollcommand=barra_x.set, yscrollcommand=barra_y.set)
    barra_x.pack(side="bottom", fill="x")
    barra_y.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    for x, y, _, _, padre in pos:
        if padre is not None:
            canvas.create_line(pos[padre][0], pos[padre][1], x, y, fill="#777", width=1.5)
    for x, y, etiqueta, tipo, _ in pos:
        relleno, borde = COLORES[tipo]
        r = medida(etiqueta) / 2
        canvas.create_oval(x - r, y - 16, x + r, y + 16, fill=relleno, outline=borde, width=1.5)
        canvas.create_text(x, y, text=etiqueta, font=("Courier", 11, "bold"))

    tk.Label(ventana, text="Cierra la ventana para continuar").pack(pady=4)
    ventana.mainloop()
    return True
