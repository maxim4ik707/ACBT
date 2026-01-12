from PyQt6.QtWidgets import QGraphicsItem, QApplication
from PyQt6.QtCore import QRectF, QPointF
from PyQt6.QtGui import QPen, QBrush, QColor
import logging

class PinGraphicsItem(QGraphicsItem):
    def __init__(self, parent_gate, pin_type, pin_index=0):
        super().__init__(parent_gate)
        self.parent_gate = parent_gate
        self.pin_type = pin_type
        self.pin_index = pin_index
        self.radius = 8
        self.connected_wires = []

        if pin_type == 'input':
            self.brush = QBrush(QColor(255, 0, 0))  # Красный - вход
        else:
            self.brush = QBrush(QColor(0, 0, 255))  # Синий - выход

        self.setZValue(10)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)

    def boundingRect(self):
        return QRectF(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def paint(self, painter, option, widget):
        painter.setBrush(self.brush)
        painter.drawEllipse(self.boundingRect())

    def get_scene_pos(self):
        """Возвращает актуальную позицию пина в координатах сцены"""
        logging.debug(f"Пин {self.pin_type} scenePos: {self.scenePos()}, mapToScene: {self.mapToScene(0, 0)}")
        return self.mapToScene(0, 0)

    def is_input(self):
        return self.pin_type == 'input'

    def is_output(self):
        return self.pin_type == 'output'

    def get_main_window(self):
        """Находит главное окно через цепочку родителей"""
        try:
            # Способ 1: Через сцену и view
            if self.scene() and self.scene().views():
                view = self.scene().views()[0]
                main_window = view.window()
                if hasattr(main_window, 'pin_clicked'):
                    return main_window

            # Способ 2: Через цепочку parentItem()
            parent = self.parentItem()
            while parent:
                if hasattr(parent, 'scene') and parent.scene():
                    views = parent.scene().views()
                    if views:
                        main_window = views[0].window()
                        if hasattr(main_window, 'pin_clicked'):
                            return main_window
                parent = parent.parentItem()

        except Exception as e:
            logging.warning(f"Ошибка поиска main_window: {e}")  # ЗАМЕНА: print → logging.warning

        return None

    def mousePressEvent(self, event):
        logging.info(
            f"Кликнут пин: {self.pin_type} на вентиле {self.parent_gate.gate.name}")  # ЗАМЕНА: print → logging.info

        main_window = self.get_main_window()
        if main_window:
            logging.debug("MainWindow найден, вызываем pin_clicked")  # ЗАМЕНА: print → logging.debug
            main_window.pin_clicked(self)
        else:
            logging.warning("MainWindow НЕ найден!")  # ЗАМЕНА: print → logging.warning

        event.accept()