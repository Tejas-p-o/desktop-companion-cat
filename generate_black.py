from PIL import Image
import os

SOURCE = "assets"
TARGET = "assets_black"

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

                # Darken the sprite
                brightness = (r + g + b) / 3

                # Very bright parts -> light cream
                if brightness > 180:
                    pixels[x, y] = (245, 238, 228, a)

                # Mid-bright parts -> dark gray highlights
                elif brightness > 120:
                    pixels[x, y] = (70, 70, 75, a)

                # Mid tones -> black fur
                elif brightness > 60:
                    pixels[x, y] = (30, 30, 35, a)

                # Very dark parts -> almost pure black
                else:
                    pixels[x, y] = (10, 10, 12, a)
                    
        img.save(os.path.join(TARGET, filename))

print("✅ Black skin generated!")