#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Contraseñas - versión nativa para Linux (Parrot OS)
Interfaz gráfica con Tkinter (viene incluido en Parrot). Sin dependencias externas.

Uso:  python3 generador.py
"""

import secrets
import string
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# ----------------------------------------------------------------------------
# Configuración de caracteres
# ----------------------------------------------------------------------------
SETS = {
    "mayus": string.ascii_uppercase,
    "minus": string.ascii_lowercase,
    "nums": string.digits,
    "simb": "!@#$%^&*()-_=+[]{};:,.?/",
}

LEET = str.maketrans({
    "a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7", "b": "8", "g": "9",
    "A": "4", "E": "3", "I": "1", "O": "0", "S": "5", "T": "7", "B": "8", "G": "9",
})

# Colores (tema oscuro)
BG = "#0f172a"
PANEL = "#1e293b"
PANEL2 = "#273449"
TEXT = "#e2e8f0"
MUTED = "#94a3b8"
ACCENT = "#38bdf8"
BORDER = "#334155"
OK = "#22c55e"
WARN = "#f59e0b"
BAD = "#ef4444"


# ----------------------------------------------------------------------------
# Lógica de generación
# ----------------------------------------------------------------------------
def pick(s):
    """Elige un carácter aleatorio de forma criptográficamente segura."""
    return s[secrets.randbelow(len(s))]


def shuffle(seq):
    """Mezcla una lista in-place usando aleatoriedad segura (Fisher-Yates)."""
    for i in range(len(seq) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        seq[i], seq[j] = seq[j], seq[i]
    return seq


def build_data_chunk(nombre, palabra, numero, fecha, usar_leet):
    """Convierte los datos introducidos por el usuario en un fragmento usable."""
    parts = []
    if nombre:
        parts.append("".join(nombre.split()))
    if palabra:
        parts.append("".join(palabra.split()))
    if numero:
        parts.append("".join(ch for ch in numero if ch.isdigit()))
    if fecha:
        # fecha es una tupla (dia, mes, anio)
        d, m, y = fecha
        if d and m and y:
            parts.append(f"{d:02d}{m:02d}{str(y)[-2:]}")  # ddmmaa

    chunk = "".join(parts)
    if usar_leet and chunk:
        chunk = chunk.translate(LEET)
    return chunk


def generate(length, sets, usar_datos, data_chunk):
    """Genera la contraseña combinando datos + aleatoriedad segura."""
    pool = "".join(sets)
    if not pool:
        return None

    chars = []

    # 1) Parte basada en los datos del usuario (máx ~55% de la longitud)
    if usar_datos and data_chunk:
        max_data = max(1, int(length * 0.55))
        for ch in data_chunk[:max_data]:
            chars.append(ch)

    # 2) Garantiza al menos un carácter de cada tipo seleccionado
    for s in sets:
        if len(chars) < length:
            chars.append(pick(s))

    # 3) Rellena el resto con aleatoriedad del conjunto completo
    while len(chars) < length:
        chars.append(pick(pool))

    # 4) Recorta si los datos ya ocupaban demasiado
    chars = chars[:length]

    shuffle(chars)
    return "".join(chars)


def estimate_strength(pw):
    """Estima la entropía en bits."""
    pool = 0
    if any(c.islower() for c in pw):
        pool += 26
    if any(c.isupper() for c in pw):
        pool += 26
    if any(c.isdigit() for c in pw):
        pool += 10
    if any(not c.isalnum() for c in pw):
        pool += 25
    import math
    return round(len(pw) * math.log2(pool)) if pool else 0


# ----------------------------------------------------------------------------
# Interfaz gráfica
# ----------------------------------------------------------------------------
class App:
    def __init__(self, root):
        self.root = root
        root.title("Generador de Contraseñas")
        root.configure(bg=BG)
        root.minsize(560, 640)

        self.historial = []
        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(".", background=BG, foreground=TEXT,
                        fieldbackground=PANEL2, bordercolor=BORDER,
                        focuscolor=ACCENT)
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=PANEL,
                        relief="flat", borderwidth=1)
        style.configure("TLabel", background=BG, foreground=TEXT)
        style.configure("Card.TLabel", background=PANEL, foreground=TEXT)
        style.configure("Muted.TLabel", background=BG, foreground=MUTED)
        style.configure("CardMuted.TLabel", background=PANEL, foreground=MUTED)
        style.configure("Title.TLabel", background=BG, foreground=TEXT,
                        font=("Sans", 15, "bold"))
        style.configure("Sub.TLabel", background=BG, foreground=MUTED,
                        font=("Sans", 9))

        style.configure("TEntry", fieldbackground=PANEL2, foreground=TEXT,
                        insertcolor=TEXT, bordercolor=BORDER, lightcolor=BORDER,
                        darkcolor=BORDER, padding=6)
        style.map("TEntry", bordercolor=[("focus", ACCENT)])

        style.configure("TSpinbox", fieldbackground=PANEL2, foreground=TEXT,
                        background=PANEL2, arrowcolor=TEXT, bordercolor=BORDER,
                        padding=4)
        style.map("TSpinbox", bordercolor=[("focus", ACCENT)])

        style.configure("TCheckbutton", background=PANEL, foreground=TEXT,
                        focuscolor=PANEL)
        style.map("TCheckbutton",
                  background=[("active", PANEL)],
                  foreground=[("active", TEXT)])

        style.configure("Accent.TButton", background=ACCENT, foreground="#04263a",
                        font=("Sans", 11, "bold"), borderwidth=0, padding=10)
        style.map("Accent.TButton",
                  background=[("active", "#0ea5e9"), ("pressed", "#0284c7")])

        style.configure("Ghost.TButton", background=PANEL2, foreground=TEXT,
                        borderwidth=1, padding=8)
        style.map("Ghost.TButton",
                  background=[("active", BORDER)])

        style.configure("TScale", background=PANEL, troughcolor=PANEL2)

        style.configure("Treeview", background=PANEL2, fieldbackground=PANEL2,
                        foreground=TEXT, bordercolor=BORDER, rowheight=24,
                        borderwidth=0)
        style.map("Treeview", background=[("selected", ACCENT)],
                  foreground=[("selected", "#04263a")])
        style.configure("Treeview.Heading", background=PANEL, foreground=MUTED,
                        relief="flat")
        style.map("Treeview.Heading", background=[("active", PANEL2)])

    def _build_ui(self):
        # Contenedor con desplazamiento (scroll)
        container = ttk.Frame(self.root)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
        vsb = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        outer = ttk.Frame(canvas, padding=20)
        win = canvas.create_window((0, 0), window=outer, anchor="nw")

        outer.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfigure(win, width=e.width))

        def _wheel_up(_e):
            canvas.yview_scroll(-1, "units")

        def _wheel_down(_e):
            canvas.yview_scroll(1, "units")

        canvas.bind_all("<Button-4>", _wheel_up)
        canvas.bind_all("<Button-5>", _wheel_down)
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(int(-e.delta / 120), "units"))

        ttk.Label(outer, text="🔐 Generador de Contraseñas",
                  style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer,
                  text="Rellena los datos que quieras usar como base; se combinan con aleatoriedad segura.",
                  style="Sub.TLabel", wraplength=500).pack(anchor="w", pady=(2, 16))

        # ---- Datos ----
        card = ttk.Frame(outer, style="Card.TFrame", padding=16)
        card.pack(fill="x")
        card.columnconfigure(1, weight=1)
        card.columnconfigure(3, weight=1)

        ttk.Label(card, text="Datos de base", style="Card.TLabel",
                  font=("Sans", 10, "bold")).grid(row=0, column=0, columnspan=4,
                                                  sticky="w", pady=(0, 10))

        # Nombre
        ttk.Label(card, text="Nombre / usuario", style="CardMuted.TLabel").grid(
            row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        self.e_nombre = ttk.Entry(card)
        self.e_nombre.grid(row=1, column=1, columnspan=3, sticky="ew", pady=4)

        # Fecha
        ttk.Label(card, text="Fecha (dd / mm / aaaa)", style="CardMuted.TLabel").grid(
            row=2, column=0, sticky="w", padx=(0, 8), pady=4)
        fecha_frame = ttk.Frame(card, style="Card.TFrame")
        fecha_frame.grid(row=2, column=1, columnspan=3, sticky="w", pady=4)
        self.sp_dia = ttk.Spinbox(fecha_frame, from_=1, to=31, width=4)
        self.sp_mes = ttk.Spinbox(fecha_frame, from_=1, to=12, width=4)
        self.sp_anio = ttk.Spinbox(fecha_frame, from_=1900, to=2100, width=6)
        self.sp_dia.set("")
        self.sp_mes.set("")
        self.sp_anio.set("")
        self.sp_dia.pack(side="left")
        ttk.Label(fecha_frame, text="/", style="CardMuted.TLabel").pack(side="left", padx=4)
        self.sp_mes.pack(side="left")
        ttk.Label(fecha_frame, text="/", style="CardMuted.TLabel").pack(side="left", padx=4)
        self.sp_anio.pack(side="left")

        # Palabra
        ttk.Label(card, text="Palabra clave / frase", style="CardMuted.TLabel").grid(
            row=3, column=0, sticky="w", padx=(0, 8), pady=4)
        self.e_palabra = ttk.Entry(card)
        self.e_palabra.grid(row=3, column=1, columnspan=3, sticky="ew", pady=4)

        # Número
        ttk.Label(card, text="Número / teléfono", style="CardMuted.TLabel").grid(
            row=4, column=0, sticky="w", padx=(0, 8), pady=4)
        self.e_numero = ttk.Entry(card)
        self.e_numero.grid(row=4, column=1, columnspan=3, sticky="ew", pady=4)

        # ---- Opciones ----
        opt = ttk.Frame(outer, style="Card.TFrame", padding=16)
        opt.pack(fill="x", pady=14)
        opt.columnconfigure(0, weight=1)
        opt.columnconfigure(1, weight=1)

        ttk.Label(opt, text="Opciones", style="Card.TLabel",
                  font=("Sans", 10, "bold")).grid(row=0, column=0, columnspan=2,
                                                  sticky="w", pady=(0, 10))

        # Longitud
        len_frame = ttk.Frame(opt, style="Card.TFrame")
        len_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        len_frame.columnconfigure(1, weight=1)
        self.len_val = tk.IntVar(value=16)
        ttk.Label(len_frame, text="Longitud:", style="Card.TLabel").grid(
            row=0, column=0, sticky="w", padx=(0, 8))
        self.scale = ttk.Scale(len_frame, from_=8, to=40, orient="horizontal",
                               variable=self.len_val, command=self._on_len)
        self.scale.grid(row=0, column=1, sticky="ew")
        self.lbl_len = ttk.Label(len_frame, text="16", style="Card.TLabel",
                                 width=3, anchor="e")
        self.lbl_len.grid(row=0, column=2, padx=(8, 0))

        # Checkboxes
        self.v_mayus = tk.BooleanVar(value=True)
        self.v_minus = tk.BooleanVar(value=True)
        self.v_nums = tk.BooleanVar(value=True)
        self.v_simb = tk.BooleanVar(value=True)
        self.v_leet = tk.BooleanVar(value=False)
        self.v_datos = tk.BooleanVar(value=True)

        checks = [
            ("Mayúsculas (A-Z)", self.v_mayus),
            ("Minúsculas (a-z)", self.v_minus),
            ("Números (0-9)", self.v_nums),
            ("Símbolos (!@#$)", self.v_simb),
            ("Sustituir letras (a→4, e→3)", self.v_leet),
            ("Incluir mis datos", self.v_datos),
        ]
        for i, (texto, var) in enumerate(checks):
            ttk.Checkbutton(opt, text=texto, variable=var).grid(
                row=2 + i // 2, column=i % 2, sticky="w", pady=3)

        # Máximo del diccionario
        max_frame = ttk.Frame(opt, style="Card.TFrame")
        max_frame.grid(row=5, column=0, columnspan=2, sticky="w", pady=(10, 0))
        ttk.Label(max_frame, text="Máx. contraseñas del diccionario:",
                  style="Card.TLabel").pack(side="left")
        self.max_var = tk.IntVar(value=100000)
        ttk.Spinbox(max_frame, from_=0, to=5000000, increment=10000,
                    width=10, textvariable=self.max_var).pack(side="left", padx=(8, 0))
        ttk.Label(max_frame, text="(0 = sin límite)", style="CardMuted.TLabel").pack(
            side="left", padx=(6, 0))

        # ---- Botón generar ----
        ttk.Button(outer, text="Generar contraseña", style="Accent.TButton",
                   command=self.on_generate).pack(fill="x")

        self.btn_dicc = ttk.Button(
            outer, text="📚 Generar diccionario de contraseñas…",
            style="Ghost.TButton", command=self.on_generar_diccionario)
        self.btn_dicc.pack(fill="x", pady=(8, 0))

        self.lbl_dicc = ttk.Label(outer, text="", style="Sub.TLabel")
        self.lbl_dicc.pack(anchor="w", pady=(6, 0))

        # Contenedor para resultado + historial (se muestran tras generar)
        self.dynamic = ttk.Frame(outer, style="TFrame")
        self.dynamic.pack(fill="x")

        # ---- Resultado ----
        self.result_frame = ttk.Frame(self.dynamic, style="Card.TFrame", padding=16)
        # se empaqueta tras generar

        res_row = ttk.Frame(self.result_frame, style="Card.TFrame")
        res_row.pack(fill="x")
        res_row.columnconfigure(0, weight=1)
        self.e_result = ttk.Entry(res_row, font=("Monospace", 13), justify="center")
        self.e_result.grid(row=0, column=0, sticky="ew")
        self.e_result.configure(state="readonly")
        ttk.Button(res_row, text="📋 Copiar", style="Ghost.TButton",
                   command=self.on_copy).grid(row=0, column=1, padx=(8, 0))

        # Barra de fuerza
        self.canvas = tk.Canvas(self.result_frame, height=8, bg=PANEL2,
                                highlightthickness=0, bd=0)
        self.canvas.pack(fill="x", pady=(12, 4))
        self.bar = self.canvas.create_rectangle(0, 0, 0, 8, fill=OK, width=0)

        info = ttk.Frame(self.result_frame, style="Card.TFrame")
        info.pack(fill="x")
        info.columnconfigure(0, weight=1)
        info.columnconfigure(1, weight=1)
        self.lbl_fuerza = ttk.Label(info, text="", style="CardMuted.TLabel")
        self.lbl_fuerza.grid(row=0, column=0, sticky="w")
        self.lbl_bits = ttk.Label(info, text="", style="CardMuted.TLabel")
        self.lbl_bits.grid(row=0, column=1, sticky="e")

        self.canvas.bind("<Configure>", lambda e: self._redraw_bar())

        # ---- Historial ----
        self.hist_frame = ttk.Frame(self.dynamic, style="Card.TFrame", padding=16)
        # se empaqueta al generar la primera contraseña

        head = ttk.Frame(self.hist_frame, style="Card.TFrame")
        head.pack(fill="x", pady=(0, 8))
        ttk.Label(head, text="Historial", style="Card.TLabel",
                  font=("Sans", 10, "bold")).pack(side="left")
        ttk.Button(head, text="🗑 Borrar", style="Ghost.TButton",
                   command=self.on_clear_history).pack(side="right")
        ttk.Button(head, text="📋 Copiar seleccionada", style="Ghost.TButton",
                   command=self.on_copy_history).pack(side="right", padx=(0, 8))

        tree_wrap = ttk.Frame(self.hist_frame, style="Card.TFrame")
        tree_wrap.pack(fill="x")
        tree_wrap.columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(tree_wrap, columns=("hora", "pw"),
                                 show="headings", height=6, selectmode="browse")
        self.tree.heading("hora", text="Hora")
        self.tree.heading("pw", text="Contraseña")
        self.tree.column("hora", width=72, anchor="center", stretch=False)
        self.tree.column("pw", anchor="w")
        self.tree.grid(row=0, column=0, sticky="ew")

        sb = ttk.Scrollbar(tree_wrap, orient="vertical", command=self.tree.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<Double-1>", lambda e: self.on_copy_history())
        self.tree.bind("<Return>", lambda e: self.on_copy_history())

        # Nota final
        ttk.Label(outer,
                  text=("Consejo: para cuentas importantes usa contraseñas 100% aleatorias y únicas, "
                        "y guárdalas en un gestor de contraseñas."),
                  style="Sub.TLabel", wraplength=500,
                  justify="left").pack(anchor="w", pady=(16, 0))

        self._last_bits_pct = 0
        self._last_color = OK

    # -- callbacks ----------------------------------------------------------
    def _on_len(self, _=None):
        self.lbl_len.configure(text=str(int(float(self.scale.get()))))

    def _redraw_bar(self):
        w = self.canvas.winfo_width()
        self.canvas.coords(self.bar, 0, 0, int(w * self._last_bits_pct / 100), 8)
        self.canvas.itemconfigure(self.bar, fill=self._last_color)

    def _selected_sets(self):
        sets = []
        if self.v_mayus.get():
            sets.append(SETS["mayus"])
        if self.v_minus.get():
            sets.append(SETS["minus"])
        if self.v_nums.get():
            sets.append(SETS["nums"])
        if self.v_simb.get():
            sets.append(SETS["simb"])
        return sets

    def on_generate(self):
        length = int(float(self.scale.get()))
        sets = self._selected_sets()
        if not sets:
            messagebox.showwarning(
                "Faltan opciones",
                "Selecciona al menos un tipo de carácter (mayúsculas, minúsculas, números o símbolos).")
            return

        def to_int(s):
            s = s.strip()
            return int(s) if s.isdigit() else 0

        fecha = (to_int(self.sp_dia.get()), to_int(self.sp_mes.get()),
                 to_int(self.sp_anio.get()))

        chunk = build_data_chunk(
            self.e_nombre.get(), self.e_palabra.get(), self.e_numero.get(),
            fecha, self.v_leet.get())

        pw = generate(length, sets, self.v_datos.get(), chunk)
        if not pw:
            return

        self.e_result.configure(state="normal")
        self.e_result.delete(0, "end")
        self.e_result.insert(0, pw)
        self.e_result.configure(state="readonly")

        # Mostrar resultado
        if not self.result_frame.winfo_ismapped():
            self.result_frame.pack(fill="x", pady=(14, 0))

        self._update_strength(pw)

        # Añadir al historial (la más reciente arriba)
        hora = datetime.datetime.now().strftime("%H:%M:%S")
        self.tree.insert("", 0, values=(hora, pw))
        self.historial.insert(0, pw)
        if not self.hist_frame.winfo_ismapped():
            self.hist_frame.pack(fill="x", pady=(14, 0))
        # Limitar a 100 entradas
        hijos = self.tree.get_children()
        if len(hijos) > 100:
            self.tree.delete(hijos[-1])
            self.historial.pop()

    def _update_strength(self, pw):
        bits = estimate_strength(pw)
        pct = min(100, round(bits / 128 * 100))
        if bits < 45:
            color, label = BAD, "Débil"
        elif bits < 70:
            color, label = WARN, "Aceptable"
        elif bits < 100:
            color, label = OK, "Fuerte"
        else:
            color, label = OK, "Muy fuerte"

        self._last_bits_pct = pct
        self._last_color = color
        self._redraw_bar()
        self.lbl_fuerza.configure(text=f"Seguridad: {label}")
        self.lbl_bits.configure(text=f"~{bits} bits")

    def _copy(self, pw):
        self.root.clipboard_clear()
        self.root.clipboard_append(pw)
        self.root.update()

    def on_copy(self):
        pw = self.e_result.get()
        if not pw:
            return
        self._copy(pw)
        self.lbl_fuerza.configure(text="✅ Copiada al portapapeles")

    def on_copy_history(self):
        sel = self.tree.selection()
        if not sel:
            hijos = self.tree.get_children()
            if not hijos:
                return
            sel = (hijos[0],)
        pw = self.tree.item(sel[0], "values")[1]
        self._copy(pw)
        self.lbl_fuerza.configure(text="✅ Copiada al portapapeles (historial)")

    def on_clear_history(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.historial.clear()

    # -- diccionario --------------------------------------------------------
    def _recoger_datos(self):
        def to_int(s):
            s = s.strip()
            return int(s) if s.isdigit() else 0
        fecha = (to_int(self.sp_dia.get()), to_int(self.sp_mes.get()),
                 to_int(self.sp_anio.get()))
        return {
            "nombre": self.e_nombre.get(),
            "palabra": self.e_palabra.get(),
            "numero": self.e_numero.get(),
            "fecha": fecha,
        }

    def on_generar_diccionario(self):
        datos = self._recoger_datos()
        if not any([datos["nombre"], datos["palabra"], datos["numero"],
                    all(datos["fecha"])]):
            messagebox.showwarning(
                "Faltan datos",
                "Introduce al menos un dato (nombre, palabra clave, número o fecha) "
                "para poder generar el diccionario.")
            return

        from tkinter import filedialog
        ruta = filedialog.asksaveasfilename(
            title="Guardar diccionario de contraseñas",
            defaultextension=".txt",
            initialfile="diccionario.txt",
            filetypes=[("Archivo de texto", "*.txt"), ("Todos los archivos", "*.*")])
        if not ruta:
            return

        try:
            limite = int(self.max_var.get())
        except (tk.TclError, ValueError):
            limite = 0

        self.btn_dicc.configure(state="disabled")
        self.lbl_dicc.configure(text="Generando diccionario…")

        import threading
        hilo = threading.Thread(target=self._worker_dicc,
                                args=(ruta, limite, datos), daemon=True)
        hilo.start()

    def _worker_dicc(self, ruta, limite, datos):
        try:
            import diccionario
            tokens = diccionario.build_tokens(**datos)
            total = 0
            with open(ruta, "w", encoding="utf-8") as f:
                for pw in diccionario.generar(tokens, limite or None):
                    f.write(pw + "\n")
                    total += 1
                    if total % 20000 == 0:
                        self.root.after(0, self._dicc_progress, total)
            self.root.after(0, self._dicc_done, total, ruta, None)
        except Exception as e:  # noqa: BLE001
            self.root.after(0, self._dicc_done, 0, ruta, str(e))

    def _dicc_progress(self, n):
        self.lbl_dicc.configure(text="Generando diccionario… %d contraseñas" % n)

    def _dicc_done(self, total, ruta, error):
        self.btn_dicc.configure(state="normal")
        if error:
            self.lbl_dicc.configure(text="Error al generar el diccionario.")
            messagebox.showerror("Error",
                                 "No se pudo generar el diccionario:\n%s" % error)
            return
        self.lbl_dicc.configure(text="Diccionario listo: %d contraseñas." % total)
        messagebox.showinfo("Diccionario generado",
                            "Se generaron %d contraseñas en:\n%s" % (total, ruta))


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
