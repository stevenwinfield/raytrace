"""
result.

The result of a render.
"""

from enum import Enum
from .environment import is_cpython
from .colour import Colour

import struct
import array

if is_cpython():
    from PyQt5.QtGui import QImage, QPixmap, QColor
    from PyQt5.QtWidgets import QApplication, QLabel, QWidget
    from PyQt5.QtCore import Qt


class ResultComponent(Enum):
    """Something which goes into a render result"""
    red = 1
    green = 2
    blue = 3
    alpha = 4
    distance = 5


class RenderResult:

    _magic = b"SAW\x00"
    _header_struct = struct.Struct("<3i")

    def __init__(self, width, height, components):
        self.width = width
        self.height = height
        self.component_index = {component: index
                                for index, component in enumerate(components)}
        size = width * height * len(components)
        self._data = array.array("d", (0.0 for _ in range(size)))
        self._row_stride = width * len(components)

    def _index(self, key):
        x, y, component = key
        return (self._row_stride * y +
                len(self.component_index) * x +
                self.component_index[component])

    def __setitem__(self, key, value):
        self._data[self._index(key)] = value

    def __getitem__(self, key):
        return self._data[self._index(key)]

    def tofile(self, fileobj):
        header = self._header_struct.pack(self.width, self.height,
                                          len(self.component_index))
        components = bytearray(component.value for
                               component, _ in sorted(
                                self.component_index.items(),
                                key=lambda pair: pair[1]))
        fileobj.write(self._magic)
        fileobj.write(header)
        fileobj.write(components)
        self._data.tofile(fileobj)

    @classmethod
    def fromfile(cls, fileobj):
        magic = fileobj.read(len(cls._magic))
        assert magic == cls._magic, "This is not a RenderResult"


        width, height, num_components = cls._header_struct.unpack(
                                        fileobj.read(cls._header_struct.size))

        components = [ResultComponent(ord(fileobj.read(1)))
                      for _ in range(num_components)]

        result = cls(width, height, components)
        result._data = array.array("d")
        result._data.fromfile(fileobj, width * height * num_components)

        return result

    def view(self, width=None, height=None):
        if is_cpython():
            r = ResultComponent.red
            g = ResultComponent.green
            b = ResultComponent.blue

            image = QImage(self.width, self.height, QImage.Format_RGB32)
            for y in range(self.height):
                for x in range(self.width):
                    colour = Colour(self[x, y, r], self[x, y, g], self[x, y, b])
                    image.setPixel(x, y, colour.rgb())

            app = QApplication.instance() or QApplication([])
            pixmap = QPixmap.fromImage(image.mirrored(vertical=True))
            label = QLabel(pixmap=pixmap)
            label.resize(width or self.width, height or self.height)
            label.setScaledContents(True)
            label.show()
            app.exec_()

        else:
            return NotImplemented
