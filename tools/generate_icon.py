"""Render the project's geometric image/PDF mark into Windows icon sizes."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

assets = Path(__file__).resolve().parents[1] / "assets"
assets.mkdir(exist_ok=True)
scale = 4
image = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

def box(coords, fill, radius=0):
    coords = tuple(value * scale for value in coords)
    draw.rounded_rectangle(coords, radius=radius * scale, fill=fill)

def polygon(coords, fill):
    draw.polygon([(x * scale, y * scale) for x, y in coords], fill=fill)

box((0, 0, 128, 128), "#2864EC", 27)
box((55, 16, 111, 112), "white", 7)
polygon([(89, 16), (111, 16), (111, 38)], "#2864EC")
polygon([(89, 16), (89, 38), (111, 38)], "#B9D1FF")
box((65, 47, 97, 51), "#CFDDF6", 2)
box((65, 57, 99, 61), "#CFDDF6", 2)
box((12, 42, 81, 99), "#1642A2", 9)
box((12, 39, 79, 95), "#68D7BB", 8)
draw.ellipse((23 * scale, 49 * scale, 36 * scale, 62 * scale), fill="white")
polygon([(18, 87), (39, 65), (51, 77), (61, 63), (74, 87)], "#146B69")
box((64, 86, 117, 111), "#EE5266", 6)
font = ImageFont.truetype("arialbd.ttf", 14 * scale)
draw.text((90.5 * scale, 98.5 * scale), "PDF", font=font, fill="white", anchor="mm")
image.save(assets / "app.png")
image.save(assets / "app.ico", sizes=[(size, size) for size in (16, 24, 32, 48, 64, 128, 256)])
image.close()
