from PIL import Image
import os

SOURCE = "assets"
TARGET = "assets_orange"

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

                # Orange tint
                brightness = (r + g + b) / 3

                if brightness > 180:
                    pixels[x, y] = (250, 245, 235, a)   # Light cream
                elif brightness < 70:
                    pixels[x, y] = (120, 70, 40, a)     # Dark brown stripes
                else:
                    pixels[x, y] = (245, 165, 70, a)    # Bright ginger orange

        img.save(os.path.join(TARGET, filename))

print("✅ Done! Orange skin generated.")