import tempfile
import time
import tkinter as tk
from pathlib import Path
from types import SimpleNamespace
from PIL import Image
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from png_a_pdf import PngToPdf


def wait(root, condition):
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        root.update()
        if condition():
            return
        time.sleep(.02)
    raise AssertionError("Timed out")


with tempfile.TemporaryDirectory() as directory:
    folder = Path(directory)
    for name, size in [("1.png", (800, 1200)), ("2.png", (1200, 700))]:
        with Image.new("RGB", size, "#2864EC") as image:
            image.save(folder / name)
    root = tk.Tk()
    app = PngToPdf(root)
    app.folder = folder
    app.scan()
    wait(root, lambda: app.photo is not None)
    root.update()
    assert app.tree.bind("<Double-1>")
    _, y, _, height = app.tree.bbox("1")
    # Real Tk double-click sequence on a row different from the initial selection.
    for moment in (1000, 1100):
        app.tree.event_generate("<ButtonPress-1>", x=100, y=y + height // 2, time=moment)
        app.tree.event_generate("<ButtonRelease-1>", x=100, y=y + height // 2, time=moment + 20)
        root.update()
    wait(root, lambda: len(app.viewers) == 1)
    viewer = next(iter(app.viewers))
    wait(root, lambda: viewer.photo is not None)
    assert viewer.path.name == "2.png"
    assert app.selected_index() == 1
    wait(root, lambda: "1200 × 700" in app.metadata.cget("text"))
    assert "1200 × 700" in viewer.info.cget("text")
    app.open_image()
    assert len(app.viewers) == 1
    viewer.window.geometry("480x360")
    root.update()
    wait(root, lambda: viewer.photo.width() <= viewer.canvas.winfo_width() - 40)
    viewer.close()
    assert len(app.viewers) == 0
    assert app.photo is not None
    app.open_image(SimpleNamespace(type=tk.EventType.ButtonPress, y=2))
    assert len(app.viewers) == 0
    (folder / "2.png").write_bytes(b"bad png")
    app.open_image()
    viewer = next(iter(app.viewers))
    wait(root, lambda: "no disponible" in viewer.info.cget("text"))
    app.close()
    assert viewer.closed
print("VIEWER_OK: double click, correct row, side preview, resize, reuse, close, invalid PNG")
