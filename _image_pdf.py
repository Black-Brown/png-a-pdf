"""Local image-folder discovery and PDF export for the desktop interface."""

import os
import re
import tempfile
from contextlib import ExitStack
from pathlib import Path


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp", ".gif"}


def discover_images(folder: Path, recursive: bool = False) -> list[Path]:
    files = folder.rglob("*") if recursive else folder.iterdir()
    return sorted(
        (p for p in files if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS),
        key=lambda p: [
            (1, int(part)) if part.isdigit() else (0, part.casefold())
            for part in re.split(r"(\d+)", p.relative_to(folder).as_posix())
        ],
    )


def images_to_pdf(paths: list[Path], destination: Path) -> None:
    """Write one page per image; preserve the destination if any input fails."""
    from PIL import Image, ImageOps

    if not paths:
        raise ValueError("Selecciona al menos una imagen.")
    if destination.resolve() in {p.resolve() for p in paths}:
        raise ValueError("El destino no puede reemplazar una imagen de origen.")
    temporary = None
    try:
        with ExitStack() as stack:
            pages = []
            for path in paths:
                try:
                    with Image.open(path) as source:
                        oriented = stack.enter_context(ImageOps.exif_transpose(source))
                        rgba = stack.enter_context(oriented.convert("RGBA"))
                        page = stack.enter_context(Image.new("RGB", rgba.size, "white"))
                        page.paste(rgba, mask=rgba.getchannel("A"))
                        pages.append(page)
                except Exception as exc:
                    raise ValueError(f"No se pudo leer {path.name}: {exc}") from exc
            with tempfile.NamedTemporaryFile(
                dir=destination.parent, suffix=".pdf", delete=False
            ) as handle:
                temporary = Path(handle.name)
            pages[0].save(temporary, "PDF", save_all=True, append_images=pages[1:], resolution=150)
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
