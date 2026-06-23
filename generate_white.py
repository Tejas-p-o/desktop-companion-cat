from PIL import Image
import os

SOURCE = "assets"
TARGET = "assets_white"

os.makedirs(TARGET, exist_ok=True)

for filename in os.listdir(SOURCE):
    if filename.lower().endswith(".png"):
        print("Processing:", filename)

        img = Image.open(os.path.join(SOURCE, filename)).convert("RGBA")
        pixels = img.load()

        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = pixels[x, y]

                if a == 0:
                    continue

                # Brighten while keeping shading
                gray = int((r + g + b) / 3)
                light = min(255, int(gray * 1.4 + 40))

                pixels[x, y] = (light, light, light, a)

        img.save(os.path.join(TARGET, filename))

print("✅ White skin generated!")