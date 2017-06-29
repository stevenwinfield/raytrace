"""
result.

The result of a render.
"""

from enum import Enum
from .environment import is_cpython
from .colour import Colour

import struct
import array

import lzma

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
        self._image = None
        self._dirty = False

    def _index(self, key):
        x, y, component = key
        return (self._row_stride * y +
                len(self.component_index) * x +
                self.component_index[component])

    def image(self):
        if is_cpython() and self._dirty:
            r = ResultComponent.red
            g = ResultComponent.green
            b = ResultComponent.blue

            image = QImage(self.width, self.height, QImage.Format_RGB32)
            for y in range(self.height):
                for x in range(self.width):
                    colour = Colour(self[x, y, r], self[x, y, g], self[x, y, b])
                    image.setPixel(x, y, colour.rgb())
            self._image = image.mirrored(vertical=True)
            self._dirty = False
        return self._image

    def __setitem__(self, key, value):
        self._data[self._index(key)] = value
        self._dirty = True

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
        compressed = lzma.LZMAFile(fileobj, "w")
        compressed.write(header)
        compressed.write(components)
        self._data.tofile(compressed)
        compressed.flush()
        compressed.close()

    @classmethod
    def fromfile(cls, fileobj):
        magic = fileobj.read(len(cls._magic))
        assert magic == cls._magic, "This is not a RenderResult"

        compressed = lzma.LZMAFile(fileobj)
        width, height, num_components = cls._header_struct.unpack(
                                        compressed.read(cls._header_struct.size))

        components = [ResultComponent(ord(compressed.read(1)))
                      for _ in range(num_components)]

        result = cls(width, height, components)
        result._data = array.array("d")
        result._data.fromfile(compressed, width * height * num_components)
        result._dirty = True
        return result

    def view(self, width=None, height=None):
        if is_cpython():
            app = QApplication.instance() or QApplication([])
            pixmap = QPixmap.fromImage(self.image())
            label = QLabel(pixmap=pixmap)
            label.resize(width or self.width, height or self.height)
            label.setScaledContents(True)
            label.show()
            app.exec_()

        else:
            return NotImplemented
