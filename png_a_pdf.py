"""Standalone PNG-to-PDF desktop application; no MarkItDown dependencies."""

import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from _image_pdf import discover_images, images_to_pdf


class PngToPdf:
    def __init__(self, root):
        self.root = root
        self.folder = None
        self.paths = []
        self.busy = False
        self.results = queue.Queue()
        root.title("PNG a PDF")
        root.geometry("760x580")
        root.minsize(580, 450)
        root.protocol("WM_DELETE_WINDOW", self.close)
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure("TButton", padding=9)
        frame = ttk.Frame(root, padding=24)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="PNG a PDF", font=("Segoe UI", 24, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Selecciona una carpeta y reúne sus imágenes PNG en un solo PDF.", wraplength=650).pack(anchor="w", pady=(4, 16))
        row = ttk.Frame(frame)
        row.pack(fill="x")
        self.choose = ttk.Button(row, text="Seleccionar carpeta…", command=self.select_folder)
        self.choose.pack(side="left")
        self.recursive = tk.BooleanVar()
        self.recursive_check = ttk.Checkbutton(row, text="Incluir subcarpetas", variable=self.recursive, command=self.scan)
        self.recursive_check.pack(side="left", padx=12)
        self.folder_label = ttk.Label(frame, text="Ninguna carpeta seleccionada", wraplength=650)
        self.folder_label.pack(anchor="w", pady=10)
        listing = ttk.Frame(frame)
        listing.pack(fill="both", expand=True)
        self.listbox = tk.Listbox(listing, font=("Segoe UI", 10), exportselection=False)
        scrollbar = ttk.Scrollbar(listing, command=self.listbox.yview)
        self.listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.listbox.pack(fill="both", expand=True)
        actions = ttk.Frame(frame)
        actions.pack(fill="x", pady=12)
        self.up = ttk.Button(actions, text="↑ Subir", command=lambda: self.move(-1))
        self.up.pack(side="left")
        self.down = ttk.Button(actions, text="↓ Bajar", command=lambda: self.move(1))
        self.down.pack(side="left", padx=6)
        self.create = ttk.Button(actions, text="Guardar PDF…", command=self.export, state="disabled")
        self.create.pack(side="right")
        self.status = tk.StringVar(value="Cada PNG será una página. Puedes cambiar el orden de la lista.")
        ttk.Label(frame, textvariable=self.status, wraplength=650).pack(anchor="w")
        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill="x", pady=(8, 0))
        root.after(100, self.poll)

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
            paths = [p for p in discover_images(self.folder, self.recursive.get()) if p.suffix.lower() == ".png"]
        except OSError as exc:
            self.paths = []
            self.refresh()
            self.create.configure(state="disabled")
            messagebox.showerror("No se pudo leer la carpeta", str(exc))
            return
        self.paths = paths
        self.folder_label.configure(text=str(self.folder))
        self.refresh()
        self.create.configure(state="normal" if paths else "disabled")
        self.status.set(f"{len(paths)} imágenes PNG encontradas. Orden: 1, 2, 3… 10.")

    def refresh(self):
        self.listbox.delete(0, "end")
        for index, path in enumerate(self.paths, 1):
            self.listbox.insert("end", f"{index:03d}   {path.relative_to(self.folder)}")

    def move(self, delta):
        if self.busy or not self.listbox.curselection():
            return
        index = self.listbox.curselection()[0]
        target = index + delta
        if 0 <= target < len(self.paths):
            self.paths[index], self.paths[target] = self.paths[target], self.paths[index]
            self.refresh()
            self.listbox.selection_set(target)
            self.listbox.see(target)

    def set_busy(self, busy):
        self.busy = busy
        for widget in (self.choose, self.recursive_check, self.up, self.down, self.create):
            widget.configure(state="disabled" if busy else "normal")
        if busy:
            self.progress.start()
        else:
            self.progress.stop()

    def export(self):
        if self.busy or not self.paths:
            return
        name = filedialog.asksaveasfilename(title="Guardar PDF", initialfile=self.folder.name + ".pdf", defaultextension=".pdf", filetypes=[("Documento PDF", "*.pdf")])
        if not name:
            return
        paths = list(self.paths)
        self.set_busy(True)
        self.status.set(f"Creando PDF con {len(paths)} páginas…")

        def work():
            try:
                images_to_pdf(paths, Path(name))
                self.results.put((True, name))
            except Exception as exc:
                self.results.put((False, str(exc)))

        threading.Thread(target=work, daemon=True).start()

    def poll(self):
        try:
            success, result = self.results.get_nowait()
        except queue.Empty:
            pass
        else:
            self.set_busy(False)
            self.status.set(f"Guardado: {result}" if success else "No se pudo crear el PDF.")
            if success:
                messagebox.showinfo("PDF creado", f"Tu PDF está listo:\n{result}")
            else:
                messagebox.showerror("Error al crear PDF", result)
        self.root.after(100, self.poll)

    def close(self):
        if self.busy:
            messagebox.showinfo("Conversión en curso", "Espera a que termine de guardar el PDF antes de cerrar.")
        else:
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
