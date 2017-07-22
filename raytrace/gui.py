from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QImage
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout


class RenderWidget(QWidget):
    def __init__(self, image_width, image_height, parent=None):
        super(RenderWidget, self).__init__(parent)
        self.image_width = image_width
        self.image_height = image_height
        self.setFixedSize(image_width, image_height)
        self.image = QImage(image_width, image_height, QImage.Format_ARGB32)
        self.image.fill(Qt.black)

    def paintEvent(self, _paint_event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

    def set_pixel(self, x, y, colour):
        self.image.setPixelColor(x, self.image_height - y - 1, colour)

    def set_pixels(self, data):
        for x, y, colour in data:
            self.set_pixel(x, y, data)


class RenderWindow(QWidget):
    def __init__(self, renderer, image_width, image_height, scene=None, camera=None, parent=None):
        super(RenderWindow, self).__init__(parent)

        self.renderer = renderer
        self.scene = scene
        self.camera = camera
        self.image_width = image_width
        self.image_height = image_height
        self.app = QApplication.instance()

        self.render_widget = RenderWidget(image_width, image_height)
        self.button = QPushButton("Render", enabled=False)

        layout = QVBoxLayout(self)
        layout.addWidget(self.render_widget)
        layout.addWidget(self.button)

        self.button.clicked.connect(self.render)

        self._pixel_count = 0
        self.update_render_button()

    def update_render_button(self):
        self.button.setEnabled(bool(self.scene and self.camera))

    def set_scene(self, scene):
        self.scene = scene
        self.update_render_button()

    def set_camera(self, camera):
        self.camera = camera
        self.update_render_button()

    def render(self):
        self._pixel_count = 0
        return self.renderer.render(self.scene, self.camera,
                                    self.image_width, self.image_height,
                                    hook=self._render_hook)

    def _render_hook(self, x, y, colour):
        self._pixel_count += 1
        self.render_widget.set_pixel(x, y, QColor(colour.rgb()))
        if self._pixel_count % 100 == 0:
            self.render_widget.repaint()
            self.app.processEvents()


