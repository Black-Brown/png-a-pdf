"""Preview bounds, transparency and corrupt-image behavior."""

import sys
import tempfile
import unittest
from pathlib import Path
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from png_a_pdf import load_preview


class PreviewTests(unittest.TestCase):
    def test_fit_preserves_ratio_and_composites_transparency(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "transparent.png"
            with Image.new("RGBA", (1200, 600), (0, 0, 0, 0)) as source:
                source.save(path)
            image, dimensions, size = load_preview(path, (300, 300))
            try:
                self.assertEqual(dimensions, (1200, 600))
                self.assertEqual(image.size, (300, 150))
                self.assertEqual(image.getpixel((0, 0)), (255, 255, 255))
                self.assertGreater(size, 0)
            finally:
                image.close()

    def test_orientation_and_invalid_image(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "rotated.png"
            with Image.new("RGB", (120, 60), "red") as source:
                exif = source.getexif()
                exif[274] = 6
                source.save(path, exif=exif)
            image, dimensions, _ = load_preview(path, (300, 300))
            try:
                self.assertEqual(dimensions, (60, 120))
            finally:
                image.close()
            path.write_bytes(b"not a png")
            with self.assertRaises(Exception):
                load_preview(path, (300, 300))


if __name__ == "__main__":
    unittest.main()
