from PyQt6.QtWidgets import QGraphicsLineItem
from PyQt6.QtCore import QLineF
from PyQt6.QtGui import QPen, QColor
import logging

class WireGraphicsItem(QGraphicsLineItem):
    def __init__(self, start_pin, end_pin):
        self.start_pin = start_pin
        self.end_pin = end_pin

        # Создаем начальную линию
        line = QLineF(start_pin.scenePos(), end_pin.scenePos())
        super().__init__(line)

        self.setPen(QPen(QColor(255, 0, 0), 3))

        # ЛОГИЧЕСКОЕ СОЕДИНЕНИЕ: связываем вентили
        self.connect_gates()

        # Добавляем провод в списки соединений пинов
        self.start_pin.connected_wires.append(self)
        self.end_pin.connected_wires.append(self)
        self.setZValue(5)
        logging.info(
            f"Провод создан: {start_pin.parent_gate.gate.name} -> {end_pin.parent_gate.gate.name}")
        # ЗАМЕНА: print → logging.info



    # wire_graphics.py - ЗАМЕНА метода connect_gates()
    def connect_gates(self):
        """Связывает выходной вентиль с входным - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        try:
            start_gate = self.start_pin.parent_gate.gate
            end_gate = self.end_pin.parent_gate.gate

            if hasattr(end_gate, 'inputs'):
                pin_index = self.end_pin.pin_index

                # Гарантируем что список inputs достаточно большой
                while len(end_gate.inputs) <= pin_index:
                    end_gate.inputs.append(None)  # Начальное значение None

                # ВАЖНО: Устанавливаем ОБЪЕКТ, а не значение
                end_gate.inputs[pin_index] = start_gate  # ← ЗАМЕНА: start_gate.get_output() → start_gate

                logging.debug(f"Соединение: {start_gate.name} -> {end_gate.name}[{pin_index}]")

        except Exception as e:
            logging.error(f"Ошибка в connect_gates: {e}")

    def update_connection(self):
        """Обновляет логическое соединение"""
        start_gate = self.start_pin.parent_gate.gate
        end_gate = self.end_pin.parent_gate.gate

        # Обновляем вход конечного вентиля
        if hasattr(end_gate, 'inputs') and end_gate.inputs:
            pin_index = self.end_pin.pin_index
            if pin_index < len(end_gate.inputs):
                end_gate.inputs[pin_index] = start_gate  # ← ЗАМЕНА: start_gate.get_output() → start_gate

    def update_position(self):
        """Обновляет позицию провода при движении вентилей - БЕЗ ЛОГИРОВАНИЯ"""
        try:
            start_pos = self.start_pin.scenePos()
            end_pos = self.end_pin.scenePos()
            new_line = QLineF(start_pos, end_pos)
            self.setLine(new_line)
            self.update()
        except Exception:
            pass  # Молча игнорируем ошибки при обновлении позиций