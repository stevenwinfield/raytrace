from vector import Vector
from ray import Ray
from primitives import Sphere
from camera import Camera, Orthographic
from scene import Scene
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtCore import Qt


x = Vector(1.0, 2.0, 3.0)
y = Vector(4.0, 3.2, 1.2)

z = x.normalized()

"""
# Vector ops
print(x + y)
print(x - y)
print(x @ y)
print(2.0 * x)
print(y * 3.0)
print(x.norm2())
print(x.norm())
print(z.norm())
print(z)
print(-z)
"""

# Ray tests

app = QApplication([])

eye = Vector(0.0, -2.0, 0.0)
forward = Vector(0.0, 1.0, 0.0)
up = Vector(0.0, 0.0, 1.0)

camera = Orthographic(eye, up, forward, 3.0, 3.0)

scene = Scene(600, 600, camera)
scene.objects.append(Sphere(Vector(-0.5, 2.0, -0.5), 0.6))
scene.objects.append(Sphere(Vector(0.5, 2.0, 0.5), 0.6))
scene.objects.append(Sphere(Vector(-0.5, 2.0, 0.5), 0.6))
scene.objects.append(Sphere(Vector(0.5, 2.0, -0.5), 0.6))
image = scene.render()

pixmap = QPixmap.fromImage(image)
label = QLabel(pixmap=pixmap)
label.show()

app.exec_()


"""
r = Ray(eye, forward, normalize=True)

#print(list(r.points(3.0, 10.0)))

s = Sphere(Vector(0.0, 0.0, 0.0), 1.0)

distance, normal = s.intersection(r)
intersection = r.point(distance)
print(distance, intersection, normal)
"""
"""
from random import random
for _ in range(100):
    x = Vector(random(), random(), random())
    y = Vector(random(), random(), random())
    z = x.cross(y)
    print(x @ z, y @ z)
"""
#print(Vector(1.0, 0.0, 0.0).cross(Vector(0.0, 1.0, 0.0)))

# print("\n".join(str(point) for point in r.points(0.0, 5.0, 0.1)))
