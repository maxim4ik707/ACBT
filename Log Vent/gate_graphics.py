from PyQt6.QtWidgets import QGraphicsItem
from PyQt6.QtCore import QRectF, Qt, QPoint
from PyQt6.QtGui import QPen, QBrush, QColor, QPainterPath

from pin_graphics import PinGraphicsItem
from logic_gates import AndGate, OrGate, NotGate,\
    InputGate, OutputGate, NandGate, NorGate, XorGate  # ← Добавил InputGate и OutputGate

import logging
class GateGraphicsItem(QGraphicsItem):
    def __init__(self, gate, width=80, height=60):
        super().__init__()
        self.gate = gate
        self.width = width
        self.height = height
        self.input_pins = []
        self.output_pins = []

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)

        self.pen = QPen(Qt.GlobalColor.black)
        self.pen.setWidth(2)
        self.brush = QBrush(QColor(200, 220, 255))

        self.create_pins()



    def get_main_window(self):
        """Находит главное окно - УЛУЧШЕННАЯ ВЕРСИЯ"""
        try:
            if self.scene() and self.scene().views():
                view = self.scene().views()[0]
                main_window = view.window()
                if hasattr(main_window, 'simulate_circuit'):
                    return main_window
        except Exception as e:
            logging.debug(f"Ошибка поиска main_window: {e}")

        return None

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            try:
                # Логируем ТОЛЬКО если вентиль действительно переместился значительно
                current_pos = self.pos()
                if not hasattr(self, '_last_logged_pos'):
                    self._last_logged_pos = current_pos

                # Логируем только если переместились больше чем на 10 пикселей
                distance = (current_pos - self._last_logged_pos).manhattanLength()
                if distance > 10:
                    logging.debug(f"Вентиль {self.gate.name} перемещен в {current_pos.x():.0f}, {current_pos.y():.0f}")
                    self._last_logged_pos = current_pos

                # Обновляем провода БЕЗ логирования
                for pin in self.input_pins + self.output_pins:
                    for wire in pin.connected_wires:
                        wire.update_position()

                # УБРАЛ ВЫЗОВ СИМУЛЯЦИИ - он вызывает рекурсию

            except Exception as e:
                logging.error(f"Ошибка при перемещении вентиля {self.gate.name}: {e}")

        return super().itemChange(change, value)
    def create_pins(self):
        """Создает входные и выходные пины. Переопределяется в дочерних классах"""
        # Базовый вариант - 2 входа, 1 выход
        self.create_input_pins(2)
        self.create_output_pins(1)

    def create_input_pins(self, count):
        """Создает указанное количество входных пинов"""
        for i in range(count):
            pin = PinGraphicsItem(self, 'input', i)
            pin.setPos(0, (i + 1) * self.height / (count + 1))
            self.input_pins.append(pin)

    def create_output_pins(self, count):
        """Создает указанное количество выходных пинов"""
        for i in range(count):
            pin = PinGraphicsItem(self, 'output', i)
            pin.setPos(self.width, (i + 1) * self.height / (count + 1))
            self.output_pins.append(pin)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawRect(0, 0, self.width, self.height)

        # Отображаем название и текущее значение
        value = self.gate.get_output()
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter,
                         f"{self.gate.name}\n{value}")


class AndGateGraphicsItem(GateGraphicsItem):
    def __init__(self):
        gate = AndGate()
        super().__init__(gate)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setBrush(self.brush)

        # AND gate - прямоугольник со скруглением только справа (увеличили радиус)
        path = QPainterPath()
        path.moveTo(0, 0)  # Левый верхний
        path.lineTo(self.width - 20, 0)  # Вправо до начала скругления
        path.arcTo(self.width - 50, 0, 50, self.height, 90, -90)  # Верхнее правое скругление (радиус 20)
        path.arcTo(self.width - 50, self.height - 50, 50, 50, 0, -90)  # Нижнее правое скругление (радиус 20)
        path.lineTo(0, self.height)  # Влево до низа
        path.closeSubpath()  # Замыкаем путь

        painter.drawPath(path)

        # Текст
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, "AND")

class OrGateGraphicsItem(GateGraphicsItem):
    def __init__(self):
        gate = OrGate()
        super().__init__(gate)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setBrush(self.brush)

        # OR gate - правильная форма с вогнутой левой стороной и острием справа
        path = QPainterPath()

        # Начинаем с левого верхнего угла
        path.moveTo(0, 0)

        # Верхняя кривая к острию справа
        path.quadTo(self.width / 2, 0, self.width, self.height / 2)

        # Нижняя кривая от острия к левому нижнему углу
        path.quadTo(self.width / 2, self.height, 0, self.height)

        # Левая вогнутая сторона - закрываем фигуру
        path.quadTo(self.width / 4, self.height / 2, 0, 0)

        painter.drawPath(path)

        # Символ OR
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, "OR")


class NotGateGraphicsItem(GateGraphicsItem):
    def __init__(self):
        gate = NotGate()
        super().__init__(gate, width=80, height=60)

    def create_pins(self):
        self.create_input_pins(1)
        self.create_output_pins(1)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setBrush(self.brush)

        # NOT gate - большой треугольник
        triangle = [
            QPoint(5, self.height // 2),  # Левая точка почти у края
            QPoint(self.width - 10, 5),  # Правая верхняя почти у края
            QPoint(self.width - 10, self.height - 5)  # Правая нижняя почти у края
        ]
        painter.drawPolygon(triangle)

        # Кружок инверсии на выходе (за треугольником)
        painter.drawEllipse(self.width - 5, self.height // 2 - 4, 8, 8)

        # Текст "NOT" - сдвинули вправо для центрирования
        font = painter.font()
        font.setBold(True)
        font.setPointSize(9)
        painter.setFont(font)

        # Черный кружок инверсии на выходе
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawEllipse(self.width - 20, self.height // 2 - 5, 10, 10)

        # Сдвигаем текст вправо для центрирования в треугольнике
        text_rect = QRectF(30, 20, 30, 20)  # Было (20, 20, 40, 20)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "NOT")


class NandGateGraphicsItem(GateGraphicsItem):
    def __init__(self):
        gate = NandGate()
        super().__init__(gate)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setBrush(self.brush)

        # NAND = AND с кружком инверсии
        path = QPainterPath()
        path.moveTo(0, 0)
        path.lineTo(self.width - 20, 0)  # Оставили место для кружка
        path.arcTo(self.width - 40, 0, 40, self.height, 90, -90)
        path.arcTo(self.width - 40, self.height - 40, 40, 40, 0, -90)
        path.lineTo(0, self.height)
        path.closeSubpath()
        painter.drawPath(path)

        # Черный кружок инверсии (как у NOT)
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawEllipse(self.width - 15, self.height // 2 - 5, 10, 10)

        # Текст
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(10, 0, self.width - 30, self.height), Qt.AlignmentFlag.AlignCenter, "NAND")


class NorGateGraphicsItem(GateGraphicsItem):
    def __init__(self):
        gate = NorGate()
        super().__init__(gate)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setBrush(self.brush)

        # NOR = OR с кружком инверсии (правильная форма OR)
        path = QPainterPath()
        path.moveTo(0, 0)
        path.quadTo(self.width / 2, 0, self.width, self.height / 2)
        path.quadTo(self.width / 2, self.height, 0, self.height)
        path.quadTo(self.width / 4, self.height / 2, 0, 0)
        painter.drawPath(path)

        # Черный кружок инверсии на выходе
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawEllipse(self.width - 20, self.height // 2 - 5, 10, 10)

        # Текст
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, "NOR")


class XorGateGraphicsItem(GateGraphicsItem):
    def __init__(self):
        gate = XorGate()
        super().__init__(gate)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setBrush(self.brush)

        # XOR = OR с дополнительной вогнутой кривой слева
        # Основная форма (как у OR)
        path = QPainterPath()
        path.moveTo(15, 0)  # Сдвигаем начало вправо для места под вторую кривую

        # Верхняя кривая
        path.quadTo(self.width / 2, 0, self.width, self.height / 2)

        # Правая сторона к низу
        path.quadTo(self.width / 2, self.height, 15, self.height)

        # Левая вогнутая сторона
        path.quadTo(self.width / 4, self.height / 2, 15, 0)

        # Вторая кривая слева (создает эффект двойной линии)
        path2 = QPainterPath()
        path2.moveTo(5, 0)
        path2.quadTo(self.width / 2 - 10, 0, self.width - 5, self.height / 2)
        path2.quadTo(self.width / 2 - 10, self.height, 5, self.height)
        path2.quadTo(self.width / 4 - 5, self.height / 2, 5, 0)

        painter.drawPath(path)
        painter.drawPath(path2)

        # Текст
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, "XOR")


class InputGateGraphicsItem(GateGraphicsItem):
    def __init__(self):
        gate = InputGate()
        super().__init__(gate, width=50, height=30)

    def create_pins(self):
        self.create_output_pins(1)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)

        # Цвет зависит от значения
        if self.gate.get_output() == 1:
            self.brush = QBrush(QColor(100, 255, 100))  # Зеленый для 1
        else:
            self.brush = QBrush(QColor(255, 100, 100))  # Красный для 0

        painter.setBrush(self.brush)
        # Input - прямоугольник со скругленными углами
        painter.drawRoundedRect(0, 0, self.width, self.height, 5, 5)
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, "IN")

class OutputGateGraphicsItem(GateGraphicsItem):
    def __init__(self):
        gate = OutputGate()
        super().__init__(gate, width=50, height=30)

    def create_pins(self):
        self.create_input_pins(1)

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)

        # Цвет зависит от значения
        if self.gate.get_output() == 1:
            self.brush = QBrush(QColor(100, 255, 100))  # Зеленый для 1
        else:
            self.brush = QBrush(QColor(255, 100, 100))  # Красный для 0

        painter.setBrush(self.brush)
        # Output - прямоугольник со скругленными углами
        painter.drawRoundedRect(0, 0, self.width, self.height, 5, 5)
        painter.drawText(self.boundingRect(), Qt.AlignmentFlag.AlignCenter, "OUT")