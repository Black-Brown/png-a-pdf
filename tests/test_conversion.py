"""Integration checks for the optional desktop image exporter."""

import tempfile
import unittest
from pathlib import Path

from PIL import Image
from pypdf import PdfReader


import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import _image_pdf as exporter


class ImagePdfTests(unittest.TestCase):
    def test_order_recursion_and_export(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            for name in ("10.png", "2.png", "1.png"):
                with Image.new("RGBA", (60, 100), (255, 0, 0, 128)) as image:
                    image.save(folder / name)
            (folder / "sub").mkdir()
            with Image.new("RGB", (100, 60)) as image:
                image.save(folder / "sub" / "extra.jpg")
            (folder / "notes.txt").write_text("ignored")
            paths = exporter.discover_images(folder)
            self.assertEqual([p.name for p in paths], ["1.png", "2.png", "10.png"])
            self.assertEqual(len(exporter.discover_images(folder, True)), 4)
            destination = folder / "output.pdf"
            exporter.images_to_pdf(paths, destination)
            reader = PdfReader(destination)
            self.assertEqual(len(reader.pages), 3)
            self.assertLess(float(reader.pages[0].mediabox.width), float(reader.pages[0].mediabox.height))

    def test_bad_image_preserves_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            bad = folder / "broken.png"
            bad.write_bytes(b"invalid image")
            destination = folder / "existing.pdf"
            destination.write_bytes(b"original")
            with self.assertRaisesRegex(ValueError, "broken.png"):
                exporter.images_to_pdf([bad], destination)
            self.assertEqual(destination.read_bytes(), b"original")
            with self.assertRaises(ValueError):
                exporter.images_to_pdf([], destination)


if __name__ == "__main__":
    unittest.main()
