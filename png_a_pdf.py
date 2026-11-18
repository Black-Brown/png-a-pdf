"""PNG a PDF desktop app: local conversion with a responsive image preview."""

import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageOps, ImageTk
from _image_pdf import discover_images, images_to_pdf

VERSION = "1.2.0"
BG = "#F4F6FA"
INK = "#18243B"
MUTED = "#718096"
LINE = "#E4E9F1"
ACCENT = "#2864EC"


def set_app_icon(window):
    assets = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "assets"
    if sys.platform == "win32":
        window.iconbitmap(str(assets / "app.ico"))
    else:
        with Image.open(assets / "app.png") as image:
            window.app_icon = ImageTk.PhotoImage(image, master=window)
        window.iconphoto(True, window.app_icon)


def load_preview(path, bounds):
    """Return an owned, bounded RGB thumbnail and metadata; no Tk calls here."""
    with Image.open(path) as source:
        oriented = ImageOps.exif_transpose(source)
        try:
            dimensions = oriented.size
            oriented.thumbnail(bounds, Image.Resampling.LANCZOS)
            rgba = oriented.convert("RGBA")
            try:
                thumbnail = Image.new("RGB", rgba.size, "white")
                with rgba.getchannel("A") as alpha:
                    thumbnail.paste(rgba, mask=alpha)
            finally:
                rgba.close()
        finally:
            oriented.close()
    return thumbnail, dimensions, path.stat().st_size


class ImageViewer:
    """A non-modal image window with a fitted, asynchronously loaded preview."""

    def __init__(self, parent, path, on_close):
        self.path = path
        self.on_close = on_close
        self.closed = False
        self.photo = None
        self.generation = 0
        self.request = None
        self.lock = threading.Lock()
        self.wake = threading.Event()
        self.results = queue.Queue()
        self.resize_job = None
        self.poll_job = None
        self.window = tk.Toplevel(parent)
        set_app_icon(self.window)
        self.window.title(f"{path.name} — PNG a PDF")
        width = min(1100, parent.winfo_screenwidth() - 100)
        height = min(850, parent.winfo_screenheight() - 120)
        self.window.geometry(f"{width}x{height}")
        self.window.minsize(480, 360)
        self.window.configure(bg=BG)
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.bind("<Escape>", lambda event: self.close())
        header = tk.Frame(self.window, bg="white", padx=20, pady=14)
        header.pack(fill="x")
        ttk.Button(header, text="Cerrar  ×", command=self.close).pack(side="right", padx=(12, 0))
        self.title = tk.Label(header, text=path.name, bg="white", fg=INK, font=("Segoe UI", 12, "bold"), anchor="w", justify="left")
        self.title.pack(side="left", fill="x", expand=True)
        header.bind("<Configure>", lambda event: self.title.configure(wraplength=max(180, event.width - 180)))
        self.canvas = tk.Canvas(self.window, bg="#EDF1F7", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True, padx=18, pady=18)
        self.info = tk.Label(self.window, text="Cargando imagen…", bg=BG, fg=MUTED, font=("Segoe UI", 10), anchor="w")
        self.info.pack(fill="x", padx=20, pady=(0, 16))
        self.canvas.bind("<Configure>", self.schedule_render)
        threading.Thread(target=self.worker, daemon=True).start()
        self.poll_job = self.window.after(60, self.poll)

    def schedule_render(self, event=None):
        if self.closed:
            return
        if self.resize_job is not None:
            self.window.after_cancel(self.resize_job)
        self.resize_job = self.window.after(140, self.render)

    def render(self):
        self.resize_job = None
        if self.closed:
            return
        self.generation += 1
        bounds = (max(100, self.canvas.winfo_width() - 40), max(100, self.canvas.winfo_height() - 40))
        with self.lock:
            self.request = (self.generation, bounds)
        self.wake.set()

    def worker(self):
        while True:
            self.wake.wait()
            with self.lock:
                if self.closed:
                    return
                request = self.request
                self.request = None
                self.wake.clear()
            if request is None:
                continue
            generation, bounds = request
            try:
                payload = load_preview(self.path, bounds)
                success = True
            except Exception as exc:
                payload, success = str(exc), False
            with self.lock:
                if self.closed:
                    if success:
                        payload[0].close()
                    return
                self.results.put((generation, success, payload))

    def poll(self):
        if self.closed:
            return
        while True:
            try:
                generation, success, payload = self.results.get_nowait()
            except queue.Empty:
                break
            if generation != self.generation:
                if success:
                    payload[0].close()
                continue
            if success:
                image, dimensions, _ = payload
                try:
                    self.photo = ImageTk.PhotoImage(image, master=self.window)
                    self.canvas.delete("all")
                    self.canvas.create_image(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, image=self.photo)
                    self.info.configure(text=f"{dimensions[0]} × {dimensions[1]} px   ·   Ajustada a la ventana   ·   Esc para cerrar")
                finally:
                    image.close()
            else:
                self.photo = None
                self.canvas.delete("all")
                self.canvas.create_text(self.canvas.winfo_width() / 2, self.canvas.winfo_height() / 2, text="No se pudo abrir esta imagen.\nComprueba que el archivo esté disponible y no esté dañado.", fill=MUTED, font=("Segoe UI", 11), justify="center", width=max(200, self.canvas.winfo_width() - 50))
                self.info.configure(text="Vista ampliada no disponible")
        self.poll_job = self.window.after(60, self.poll)

    def close(self):
        if self.closed:
            return
        with self.lock:
            self.closed = True
            self.wake.set()
        for job in (self.resize_job, self.poll_job):
            if job is not None:
                self.window.after_cancel(job)
        while True:
            try:
                _, success, payload = self.results.get_nowait()
                if success:
                    payload[0].close()
            except queue.Empty:
                break
        self.photo = None
        self.window.destroy()
        self.on_close(self)


class PngToPdf:
    def __init__(self, root):
        self.root = root
        self.folder = None
        self.paths = []
        self.busy = False
        self.results = queue.Queue()
        self.preview_results = queue.Queue()
        self.preview_request = None
        self.preview_lock = threading.Lock()
        self.preview_event = threading.Event()
        self.preview_generation = 0
        self.resize_job = None
        self.photo = None
        self.closed = False
        self.viewers = set()
        self.recursive = tk.BooleanVar()
        self.status = tk.StringVar(value="Elige una carpeta para comenzar.")
        root.title(f"PNG a PDF · {VERSION}")
        set_app_icon(root)
        root.geometry("1160x760")
        root.minsize(960, 640)
        root.configure(bg=BG)
        root.protocol("WM_DELETE_WINDOW", self.close)
        self.configure_styles()
        self.build()
        threading.Thread(target=self.preview_worker, daemon=True).start()
        root.after(80, self.poll)
        root.bind("<Control-o>", lambda event: self.select_folder())
        root.bind("<Control-s>", lambda event: self.export())

    def configure_styles(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10), padding=(14, 10), background="white", foreground=INK, bordercolor=LINE, focuscolor=LINE, lightcolor="white", darkcolor="white")
        style.map("TButton", background=[("active", "#F0F4FB")], foreground=[("disabled", "#A5AFBE")])
        style.configure("Primary.TButton", background=ACCENT, foreground="white", bordercolor=ACCENT, lightcolor=ACCENT, darkcolor=ACCENT, font=("Segoe UI", 10, "bold"))
        style.map("Primary.TButton", background=[("disabled", "#D7E2F9"), ("active", "#1E51C6")], foreground=[("disabled", "#8CA5D3")])
        style.configure("TCheckbutton", font=("Segoe UI", 10), background="white", foreground=MUTED, focuscolor="white")
        style.map("TCheckbutton", background=[("active", "white")])
        style.configure("Images.Treeview", font=("Segoe UI", 10), rowheight=52, background="white", fieldbackground="white", foreground=INK, borderwidth=0, relief="flat")
        style.map("Images.Treeview", background=[("selected", "#EAF1FF")], foreground=[("selected", "#2053BF")])
        style.configure("Images.Treeview.Heading", font=("Segoe UI", 9), background="#F8FAFD", foreground=MUTED, borderwidth=0, padding=(8, 8), relief="flat")
        style.layout("Images.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        style.configure("TScrollbar", background="#D3DBE8", troughcolor="white", borderwidth=0, arrowsize=12)
        style.configure("Horizontal.TProgressbar", background=ACCENT, troughcolor=BG, borderwidth=0, thickness=3)

    def label(self, parent, text="", size=10, color=INK, bold=False, bg="white", **kwargs):
        return tk.Label(parent, text=text, font=("Segoe UI", size, "bold" if bold else "normal"), bg=bg, fg=color, **kwargs)

    def build(self):
        sidebar = tk.Frame(self.root, bg="#142039", width=190)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        mark = tk.Canvas(sidebar, width=42, height=42, bg="#142039", highlightthickness=0)
        mark.pack(anchor="w", padx=24, pady=(30, 10))
        assets = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "assets"
        with Image.open(assets / "app.png") as logo:
            self.brand_icon = ImageTk.PhotoImage(logo.resize((42, 42), Image.Resampling.LANCZOS), master=self.root)
        mark.create_image(21, 21, image=self.brand_icon)
        self.label(sidebar, "PNG a PDF", 17, "white", True, "#142039").pack(anchor="w", padx=24)
        self.label(sidebar, "Tu espacio de conversión", 9, "#9CAEC9", bg="#142039").pack(anchor="w", padx=24, pady=(5, 36))
        self.label(sidebar, "HERRAMIENTAS", 8, "#8EA1C0", True, "#142039").pack(anchor="w", padx=24, pady=(0, 12))
        selected = tk.Frame(sidebar, bg="#243858")
        selected.pack(fill="x", padx=12)
        self.label(selected, "▧   Imágenes a PDF", 10, "#EAF1FF", True, "#243858", padx=12, pady=12).pack(anchor="w")
        footer = tk.Frame(sidebar, bg="#142039")
        footer.pack(side="bottom", fill="x", padx=24, pady=24)
        self.label(footer, "●  Procesamiento local", 9, "#80D6BA", bg="#142039").pack(anchor="w")
        self.label(footer, f"Versión {VERSION}", 9, "#8EA1C0", bg="#142039").pack(anchor="w", pady=(8, 0))

        main = tk.Frame(self.root, bg=BG, padx=28, pady=26)
        main.pack(fill="both", expand=True)
        header = tk.Frame(main, bg=BG)
        header.pack(fill="x")
        self.label(header, "ESPACIO DE TRABAJO", 9, MUTED, True, BG).pack(anchor="w")
        title = tk.Frame(header, bg=BG)
        title.pack(fill="x", pady=(8, 0))
        self.label(title, "Imágenes a PDF", 26, INK, True, BG).pack(side="left")
        self.create = ttk.Button(title, text="Exportar PDF  →", style="Primary.TButton", command=self.export, state="disabled")
        self.create.pack(side="right")
        self.label(header, "Organiza tus imágenes, revisa cada página y crea tu documento.", 10, MUTED, bg=BG).pack(anchor="w", pady=(6, 20))

        toolbar = tk.Frame(main, bg="white", highlightbackground=LINE, highlightcolor=LINE, highlightthickness=1, padx=16, pady=12)
        toolbar.pack(fill="x", pady=(0, 18))
        self.choose = ttk.Button(toolbar, text="＋  Elegir carpeta", command=self.select_folder)
        self.choose.pack(side="left")
        self.recursive_check = ttk.Checkbutton(toolbar, text="Incluir subcarpetas", variable=self.recursive, command=self.scan)
        self.recursive_check.pack(side="left", padx=16)
        self.count = self.label(toolbar, "0 imágenes", 10, ACCENT, True)
        self.count.pack(side="right")

        body = tk.Frame(main, bg=BG)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=4, minsize=270)
        body.columnconfigure(1, weight=6, minsize=350)
        body.rowconfigure(0, weight=1)
        left = tk.Frame(body, bg="white", highlightbackground=LINE, highlightcolor=LINE, highlightthickness=1)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        left_header = tk.Frame(left, bg="white", padx=16, pady=16)
        left_header.pack(fill="x")
        self.label(left_header, "Tus imágenes", 12, bold=True).pack(anchor="w")
        self.folder_label = self.label(left_header, "Sin carpeta seleccionada", 9, MUTED, anchor="w")
        self.folder_label.pack(fill="x", pady=(5, 0))
        tk.Frame(left, bg=LINE, height=1).pack(fill="x")
        listing = tk.Frame(left, bg="white")
        listing.pack(fill="both", expand=True, padx=6, pady=6)
        self.tree = ttk.Treeview(listing, columns=("page", "name"), show="headings", selectmode="browse", style="Images.Treeview", height=4)
        self.tree.heading("page", text="Pág.")
        self.tree.heading("name", text="Archivo PNG")
        self.tree.column("page", width=50, stretch=False, anchor="center")
        self.tree.column("name", width=190, minwidth=100)
        scroll = ttk.Scrollbar(listing, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.selection_changed)
        self.tree.bind("<Double-1>", self.open_image)
        self.tree.bind("<Return>", self.open_image)
        self.empty_list = self.label(listing, "Tu próxima página\nempieza aquí.\n\nElige una carpeta con PNG.", 11, MUTED, justify="center")
        self.empty_list.place(relx=.5, rely=.45, anchor="center")
        actions = tk.Frame(left, bg="white", padx=12, pady=12)
        actions.pack(fill="x")
        self.up = ttk.Button(actions, text="↑ Subir", command=lambda: self.move(-1), state="disabled")
        self.up.pack(side="left")
        self.down = ttk.Button(actions, text="↓ Bajar", command=lambda: self.move(1), state="disabled")
        self.down.pack(side="left", padx=(8, 0))

        right = tk.Frame(body, bg="white", highlightbackground=LINE, highlightcolor=LINE, highlightthickness=1)
        right.grid(row=0, column=1, sticky="nsew")
        preview_header = tk.Frame(right, bg="white", padx=16, pady=16)
        preview_header.pack(fill="x")
        self.label(preview_header, "Vista previa", 12, bold=True).pack(side="left")
        self.page_label = self.label(preview_header, "SIN SELECCIÓN", 8, MUTED, True)
        self.page_label.pack(side="right")
        self.canvas = tk.Canvas(right, bg="#EDF1F7", highlightthickness=0, height=180)
        self.canvas.pack(fill="both", expand=True, padx=14)
        self.canvas.bind("<Configure>", self.schedule_preview)
        self.canvas.bind("<Double-1>", lambda event: self.open_image())
        details = tk.Frame(right, bg="white", padx=16, pady=16)
        details.pack(fill="x")
        self.filename = self.label(details, "Selecciona una imagen", 11, bold=True, anchor="w")
        self.filename.pack(fill="x")
        self.metadata = self.label(details, "La vista previa aparecerá aquí.", 9, MUTED, anchor="w")
        self.metadata.pack(fill="x", pady=(5, 0))
        self.label(details, "Doble clic en una imagen para verla en grande", 9, ACCENT, anchor="w").pack(fill="x", pady=(7, 0))
        right.bind("<Configure>", lambda e: self.filename.configure(wraplength=max(180, e.width - 40)))
        self.show_placeholder()
        self.progress_host = tk.Frame(main, bg=BG, height=4)
        self.progress_host.pack(fill="x", pady=(18, 8))
        self.progress = ttk.Progressbar(self.progress_host, mode="indeterminate")
        self.label(main, size=9, color=MUTED, bg=BG, textvariable=self.status, anchor="w", wraplength=770).pack(fill="x")

    def selected_index(self):
        selected = self.tree.selection()
        return int(selected[0]) if selected else None

    def open_image(self, event=None):
        if event is not None and event.type == tk.EventType.ButtonPress:
            row = self.tree.identify_row(event.y)
            if not row:
                return "break"
            self.tree.selection_set(row)
            self.tree.focus(row)
        index = self.selected_index()
        if index is None or index >= len(self.paths):
            return "break"
        path = self.paths[index]
        for viewer in self.viewers:
            if viewer.path == path and not viewer.closed:
                viewer.window.deiconify()
                viewer.window.lift()
                viewer.window.focus_set()
                return "break"
        viewer = ImageViewer(self.root, path, self.viewers.discard)
        self.viewers.add(viewer)
        return "break"

    def select_folder(self):
        if self.busy:
            return
        name = filedialog.askdirectory(title="Selecciona una carpeta con imágenes PNG")
        if name:
            self.folder = Path(name)
            self.scan()

    def scan(self):
        if self.busy or self.folder is None:
            return
        try:
            self.paths = [p for p in discover_images(self.folder, self.recursive.get()) if p.suffix.lower() == ".png"]
        except OSError as exc:
            self.paths = []
            self.refresh()
            self.status.set("No se pudo leer la carpeta.")
            messagebox.showerror("Carpeta no disponible", str(exc))
            return
        self.folder_label.configure(text=self.folder.name)
        self.refresh(0 if self.paths else None)
        self.status.set(f"{len(self.paths)} imágenes encontradas · Orden numérico · Selecciona una para revisarla." if self.paths else "Esta carpeta no contiene imágenes PNG. Prueba incluyendo las subcarpetas.")

    def refresh(self, selection=None):
        self.tree.delete(*self.tree.get_children())
        for index, path in enumerate(self.paths):
            self.tree.insert("", "end", iid=str(index), values=(f"{index + 1:02}", str(path.relative_to(self.folder))))
        self.count.configure(text=f"{len(self.paths)} imágenes")
        if self.paths:
            self.empty_list.place_forget()
        else:
            self.empty_list.place(relx=.5, rely=.45, anchor="center")
        if selection is not None:
            self.tree.selection_set(str(selection))
            self.tree.focus(str(selection))
            self.tree.see(str(selection))
        self.selection_changed()
        self.update_controls()

    def selection_changed(self, event=None):
        self.update_controls()
        self.queue_preview()

    def move(self, delta):
        index = self.selected_index()
        if self.busy or index is None:
            return
        target = index + delta
        if 0 <= target < len(self.paths):
            self.paths[index], self.paths[target] = self.paths[target], self.paths[index]
            self.refresh(target)

    def update_controls(self):
        index = self.selected_index()
        self.create.configure(state="normal" if self.paths and not self.busy else "disabled")
        self.up.configure(state="normal" if not self.busy and index is not None and index > 0 else "disabled")
        self.down.configure(state="normal" if not self.busy and index is not None and index < len(self.paths) - 1 else "disabled")

    def show_placeholder(self, text="Selecciona una imagen\npara ver su vista previa"):
        self.canvas.delete("all")
        self.photo = None
        width = max(300, self.canvas.winfo_width())
        height = max(200, self.canvas.winfo_height())
        self.canvas.create_text(width / 2, height / 2, text=text, fill=MUTED, font=("Segoe UI", 11), justify="center", width=max(200, width - 50), tags="placeholder")

    def schedule_preview(self, event=None):
        if self.resize_job is not None:
            self.root.after_cancel(self.resize_job)
        self.resize_job = self.root.after(140, self.resized_preview)

    def resized_preview(self):
        self.resize_job = None
        self.queue_preview()

    def queue_preview(self):
        self.preview_generation += 1
        index = self.selected_index()
        if index is None or index >= len(self.paths):
            self.page_label.configure(text="SIN SELECCIÓN")
            self.filename.configure(text="Selecciona una imagen")
            self.metadata.configure(text="La vista previa aparecerá aquí.")
            self.show_placeholder()
            return
        path = self.paths[index]
        self.page_label.configure(text=f"PÁGINA {index + 1} DE {len(self.paths)}")
        self.filename.configure(text=path.name)
        self.metadata.configure(text="Cargando vista previa…")
        self.show_placeholder("Cargando imagen…")
        bounds = (max(100, self.canvas.winfo_width() - 48), max(100, self.canvas.winfo_height() - 40))
        with self.preview_lock:
            self.preview_request = (self.preview_generation, path, bounds)
        self.preview_event.set()

    def preview_worker(self):
        while True:
            self.preview_event.wait()
            if self.closed:
                return
            with self.preview_lock:
                request = self.preview_request
                self.preview_request = None
                self.preview_event.clear()
            if request is None:
                continue
            generation, path, bounds = request
            try:
                payload = load_preview(path, bounds)
                self.preview_results.put((generation, True, payload))
            except Exception as exc:
                self.preview_results.put((generation, False, str(exc)))

    def receive_preview(self):
        while True:
            try:
                generation, success, payload = self.preview_results.get_nowait()
            except queue.Empty:
                break
            if generation != self.preview_generation:
                if success:
                    payload[0].close()
                continue
            if not success:
                self.show_placeholder("No se pudo abrir esta imagen.\nComprueba que el PNG no esté dañado.")
                self.metadata.configure(text="Vista previa no disponible")
                continue
            image, dimensions, size = payload
            try:
                self.photo = ImageTk.PhotoImage(image, master=self.root)
                width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
                x, y = width / 2, height / 2
                self.canvas.delete("all")
                self.canvas.create_rectangle(x - image.width / 2 + 3, y - image.height / 2 + 4, x + image.width / 2 + 3, y + image.height / 2 + 4, fill="#D6DDE9", outline="")
                self.canvas.create_image(x, y, image=self.photo)
                readable = f"{size / 1024 / 1024:.1f} MB" if size >= 1024 * 1024 else f"{size / 1024:.0f} KB"
                self.metadata.configure(text=f"{dimensions[0]} × {dimensions[1]} px   ·   PNG   ·   {readable}")
            finally:
                image.close()

    def set_busy(self, busy):
        self.busy = busy
        for widget in (self.choose, self.recursive_check):
            widget.configure(state="disabled" if busy else "normal")
        self.update_controls()
        if busy:
            self.progress.place(x=0, y=0, relwidth=1, relheight=1)
            self.progress.start()
        else:
            self.progress.stop()
            self.progress.place_forget()

    def export(self):
        if self.busy or not self.paths:
            return
        name = filedialog.asksaveasfilename(title="Guardar PDF", initialfile=self.folder.name + ".pdf", defaultextension=".pdf", filetypes=[("Documento PDF", "*.pdf")])
        if not name:
            return
        paths = list(self.paths)
        self.set_busy(True)
        self.status.set(f"Creando tu PDF con {len(paths)} páginas…")

        def work():
            try:
                images_to_pdf(paths, Path(name))
                self.results.put((True, name))
            except Exception as exc:
                self.results.put((False, str(exc)))

        threading.Thread(target=work, daemon=True).start()

    def poll(self):
        if self.closed:
            return
        self.receive_preview()
        try:
            success, result = self.results.get_nowait()
        except queue.Empty:
            pass
        else:
            self.set_busy(False)
            self.status.set(f"PDF guardado en {result}" if success else "No se pudo crear el PDF.")
            if success:
                messagebox.showinfo("Tu PDF está listo", f"Archivo guardado en:\n{result}")
            else:
                messagebox.showerror("Error al crear PDF", result)
        self.root.after(80, self.poll)

    def close(self):
        if self.busy:
            messagebox.showinfo("Conversión en curso", "Espera a que termine de guardar el PDF antes de cerrar.")
            return
        self.closed = True
        self.preview_event.set()
        for viewer in list(self.viewers):
            viewer.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    PngToPdf(root)
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "--convert":
        folder, destination = Path(sys.argv[2]), Path(sys.argv[3])
        images_to_pdf([p for p in discover_images(folder) if p.suffix.lower() == ".png"], destination)
    else:
        main()
