"""
scene.

Defines the Scene class.
"""

from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt

INFINITY = float("inf")

class Scene:
    """Scene class."""

    def __init__(self, width=None, height=None, camera=None):
        self.width = width
        self.height = height
        self.camera = camera
        self.lights = []
        self.objects = []

    def render(self):
        image = QImage(self.width, self.height, QImage.Format_RGB32)
        image.fill(Qt.black)

        for x, y, ray in self.camera.rays(self.width, self.height):
            #print(x, y, ray)
            min_distance = INFINITY
            min_normal = None
            for obj in self.objects:
                distance, normal = obj.intersection(ray)
                if distance is None:
                    continue
                elif distance < min_distance:
                    min_distance = distance
                    min_normal = normal

            if min_distance == INFINITY:
                continue
            #print("    ", min_distance)
            shade = int(-ray.direction @ min_normal * 255)
            image.setPixel(x, y, 0x010101 * shade)

        return image
