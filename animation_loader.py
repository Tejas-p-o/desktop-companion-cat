import os
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


def load_frames(name, scale=120, skin="assets_grey"):
    frames = []
    i = 1

    while True:
        path = os.path.join(skin, f"{name} ({i}).png")

        if not os.path.exists(path):
            break

        pixmap = QPixmap(path).scaled(
            scale,
            scale,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        frames.append(pixmap)
        i += 1

    return frames