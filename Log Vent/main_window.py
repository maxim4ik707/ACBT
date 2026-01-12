from PyQt6.QtWidgets import (QMainWindow, QGraphicsView, QGraphicsScene,
                             QToolBar, QPushButton, QVBoxLayout, QWidget,
                             QDockWidget, QMessageBox)
from PyQt6.QtGui import QPainter, QAction, QColor, QPen, QBrush
from PyQt6.QtCore import Qt

from pin_graphics import PinGraphicsItem
from wire_graphics import WireGraphicsItem
from gate_graphics import (AndGateGraphicsItem, OrGateGraphicsItem, NotGateGraphicsItem,
                          InputGateGraphicsItem, OutputGateGraphicsItem,
                          NandGateGraphicsItem, NorGateGraphicsItem, XorGateGraphicsItem)  # Добавил новые  # ← Добавил новые классы
from logic_gates import AndGate, OrGate, NotGate, InputGate, OutputGate  # ← Добавил InputGate

from truth_table import TruthTableWidget
import logging
import random
from datetime import datetime

# Настройка логирования - ОДИН ФАЙЛ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('circuit_simulator.log', mode='w')
    ]
)

# Уровни логирования:
# DEBUG - отладочная информация (много сообщений)
# INFO - основная информация (умеренно)
# WARNING - предупреждения (мало сообщений)
# ERROR - ошибки (очень мало сообщений)

LOG_LEVEL = logging.DEBUG # Меняй этот уровень по необходимости


class GraphicsView(QGraphicsView):
    def __init__(self, scene, main_window):
        super().__init__(scene)
        self.main_window = main_window
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

    def mouseReleaseEvent(self, event):
        # После перемещения вентилей запускаем симуляцию
        super().mouseReleaseEvent(event)
        self.main_window.simulate_circuit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_pin = None
        self.dragging_gate = None  # Для перетаскивания новых вентилей с панели
        self.init_ui()

    # main_window.py - ДОБАВЛЯЕМ в начало класса MainWindow (после __init__)

    def setup_styles(self):
        """Настраивает стили для всех элементов интерфейса"""
        # Стиль для главного окна
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }

            QDockWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-weight: bold;
                padding: 5px;
            }

            QDockWidget::title {
                background-color: #4a86e8;
                color: white;
                padding: 5px;
                border-radius: 3px;
            }

            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
                margin: 2px;
            }

            QPushButton:hover {
                background-color: #3a76d8;
            }

            QPushButton:pressed {
                background-color: #2a66c8;
            }

            QPushButton#clear_button {
                background-color: #e74c3c;
                margin-top: 10px;
            }

            QPushButton#clear_button:hover {
                background-color: #c0392b;
            }

            QTableWidget {
                background-color: white;
                border: 1px solid #cccccc;
                gridline-color: #e0e0e0;
                font-family: "Segoe UI", Arial;
            }

            QTableWidget::item {
                padding: 5px;
            }

            QHeaderView::section {
                background-color: #4a86e8;
                color: white;
                padding: 5px;
                border: none;
                font-weight: bold;
            }

            QGraphicsView {
                background-color: white;
                border: 2px solid #cccccc;
                border-radius: 5px;
            }
        """)

    def init_ui(self):
        # main_window.py - В init_ui() добавляем после создания центрального виджета

        self.setup_styles()  # Вызываем настройку стилей

        self.setWindowTitle("Logic Gate Simulator")
        self.setGeometry(100, 100, 1400, 900)

        # Создаем графическую сцену
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 1200, 600)  # Уменьшили высоту сцены

        # Создаем представление для сцены
        self.view = GraphicsView(self.scene, self)
        # Добавляем сетку на сцену
        self.add_grid_to_scene()

        # Создаем таблицу истинности
        self.truth_table = TruthTableWidget(self)
        # main_window.py - ДОБАВЬ эту строку в init_ui() после создания truth_table
        self.truth_table.update_button.clicked.connect(self.force_simulation_update)
        # Основной layout
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.view, 70)  # 70% места для схемы
        main_layout.addWidget(self.truth_table, 30)  # 30% для таблицы

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Создаем панель инструментов
        self.create_toolbar()
        #self.add_test_gates()

    # И добавляем метод в класс MainWindow:
    def add_grid_to_scene(self):
        """Добавляет сетку на сцену для удобства позиционирования"""
        from PyQt6.QtGui import QPen, QBrush
        from PyQt6.QtCore import Qt

        # Рисуем сетку
        pen = QPen(QColor(230, 230, 230))
        pen.setWidth(1)

        grid_size = 20  # Размер ячейки сетки

        # Вертикальные линии
        for x in range(0, int(self.scene.sceneRect().width()), grid_size):
            self.scene.addLine(x, 0, x, self.scene.sceneRect().height(), pen)

        # Горизонтальные линии
        for y in range(0, int(self.scene.sceneRect().height()), grid_size):
            self.scene.addLine(0, y, self.scene.sceneRect().width(), y, pen)

    def create_toolbar(self):


        """Создает панель инструментов с вентилями"""
        dock = QDockWidget("Components", self)
        dock.setFixedWidth(150)

        widget = QWidget()
        layout = QVBoxLayout()

        # Создаем кнопки для разных вентилей
        btn_input = QPushButton("INPUT")  # ← Новая кнопка
        btn_output = QPushButton("OUTPUT")  # ← Новая кнопка
        btn_and = QPushButton("AND Gate")
        btn_or = QPushButton("OR Gate")
        btn_not = QPushButton("NOT Gate")
        btn_nand = QPushButton("NAND Gate")
        btn_nor = QPushButton("NOR Gate")
        btn_xor = QPushButton("XOR Gate")

        # Подключаем кнопки к созданию вентилей
        btn_input.clicked.connect(lambda: self.create_gate("INPUT"))  # ← Новый обработчик
        btn_output.clicked.connect(lambda: self.create_gate("OUTPUT"))  # ← Новый обработчик
        btn_and.clicked.connect(lambda: self.create_gate("AND"))
        btn_or.clicked.connect(lambda: self.create_gate("OR"))
        btn_not.clicked.connect(lambda: self.create_gate("NOT"))
        btn_nand.clicked.connect(lambda: self.create_gate("NAND"))
        btn_nor.clicked.connect(lambda: self.create_gate("NOR"))
        btn_xor.clicked.connect(lambda: self.create_gate("XOR"))

        # Добавляем кнопки в layout
        layout.addWidget(btn_input)  # ← Добавляем в layout
        layout.addWidget(btn_output)  # ← Добавляем в layout
        layout.addWidget(btn_and)
        layout.addWidget(btn_or)
        layout.addWidget(btn_not)
        layout.addWidget(btn_nand)
        layout.addWidget(btn_nor)
        layout.addWidget(btn_xor)
        layout.addStretch()

        widget.setLayout(layout)
        dock.setWidget(widget)

        # main_window.py - ДОБАВЬ в метод create_toolbar() после создания кнопок вентилей

        # Кнопка очистки поля с ID для стиля
        btn_clear = QPushButton("🗑️ Очистить поле")
        btn_clear.setObjectName("clear_button")  # Устанавливаем ID для CSS
        btn_clear.clicked.connect(self.clear_scene)
        layout.addSpacing(20)  # Отступ сверху
        layout.addWidget(btn_clear)

        # Добавляем разделитель перед кнопкой очистки
        layout.addSpacing(20)  # Отступ сверху

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    # И ДОБАВЬ этот метод в класс MainWindow:
    def force_simulation_update(self):
        """Принудительно обновляет симуляцию перед анализом"""
        self.simulate_circuit()

    # main_window.py - ДОБАВЛЯЕМ метод в класс MainWindow

    def find_free_position(self, width, height):
        """Находит свободное место для нового вентиля на сцене"""
        # Используем сетку для аккуратного размещения
        grid_size = 20
        scene_rect = self.scene.sceneRect()

        # Начинаем поиск с левого верхнего угла видимой области
        view_rect = self.view.mapToScene(self.view.viewport().geometry()).boundingRect()
        start_x = max(50, view_rect.x())
        start_y = max(50, view_rect.y())

        # Пытаемся найти свободное место, двигаясь по сетке
        for attempt in range(10):  # 10 попыток в основной области
            for y_offset in range(0, 400, grid_size * 3):  # Ищем в пределах 400px по вертикали
                for x_offset in range(0, 400, grid_size * 3):  # И в пределах 400px по горизонтали
                    x = start_x + x_offset
                    y = start_y + y_offset

                    # Проверяем, чтобы вентиль не выходил за границы сцены
                    if x + width > scene_rect.width() - 50:
                        continue
                    if y + height > scene_rect.height() - 50:
                        continue

                    # Создаем временный прямоугольник для проверки коллизий
                    temp_rect = self.scene.addRect(x, y, width, height,
                                                   QPen(Qt.GlobalColor.transparent),
                                                   QBrush(Qt.GlobalColor.transparent))
                    colliding_items = temp_rect.collidingItems()
                    self.scene.removeItem(temp_rect)

                    # Фильтруем только значимые коллизии (вентили и провода)
                    significant_collisions = []
                    for item in colliding_items:
                        # Проверяем, что это не фоновая сетка и не сам временный прямоугольник
                        if (hasattr(item, 'gate') or  # Вентили
                                isinstance(item, WireGraphicsItem) or  # Провода
                                (hasattr(item, 'parent_gate') and hasattr(item, 'pin_type'))):  # Пины
                            significant_collisions.append(item)

                    # Если нет значимых коллизий - место свободно
                    if not significant_collisions:
                        return x, y

        # Если не нашли свободного места в основной области, пробуем найти любое место с минимальным перекрытием
        best_position = None
        min_collisions = float('inf')

        # Пробуем несколько случайных позиций
        for attempt in range(20):
            x = start_x + random.randint(0, 300)
            y = start_y + random.randint(0, 300)

            # Проверяем границы
            if x + width > scene_rect.width() - 50 or y + height > scene_rect.height() - 50:
                continue

            # Проверяем коллизии
            temp_rect = self.scene.addRect(x, y, width, height,
                                           QPen(Qt.GlobalColor.transparent),
                                           QBrush(Qt.GlobalColor.transparent))
            colliding_items = temp_rect.collidingItems()
            self.scene.removeItem(temp_rect)

            # Считаем значимые коллизии
            significant_count = 0
            for item in colliding_items:
                if (hasattr(item, 'gate') or
                        isinstance(item, WireGraphicsItem) or
                        (hasattr(item, 'parent_gate') and hasattr(item, 'pin_type'))):
                    significant_count += 1

            if significant_count < min_collisions:
                min_collisions = significant_count
                best_position = (x, y)

            # Если нашли место с 1 или 0 коллизиями - используем его
            if significant_count <= 1:
                return x, y

        # Если ничего не нашли, возвращаем лучшее найденное место или центр
        if best_position:
            return best_position

        # Последний вариант - центр видимой области
        return view_rect.center().x() - width / 2, view_rect.center().y() - height / 2

    def create_gate(self, gate_type):
        """Создает новый вентиль с интеллектуальным позиционированием"""
        logging.info(f"Создание вентиля: {gate_type}")

        # Создаем вентиль
        gate_constructors = {
            "AND": AndGateGraphicsItem,
            "OR": OrGateGraphicsItem,
            "NOT": NotGateGraphicsItem,
            "INPUT": InputGateGraphicsItem,
            "OUTPUT": OutputGateGraphicsItem,
            "NAND": NandGateGraphicsItem,
            "NOR": NorGateGraphicsItem,
            "XOR": XorGateGraphicsItem
        }

        if gate_type not in gate_constructors:
            logging.warning(f"Неизвестный тип вентиля: {gate_type}")
            return

        # Создаем экземпляр вентиля
        new_gate = gate_constructors[gate_type]()
        logging.debug(f"Вентиль {gate_type} создан")

        # Используем интеллектуальное позиционирование
        pos = self.find_free_position(new_gate.width, new_gate.height)
        new_gate.setPos(pos[0], pos[1])
        new_gate.setZValue(10)

        # Добавляем на сцену
        self.scene.addItem(new_gate)

        logging.info(f"Вентиль {gate_type} размещен в ({int(pos[0])}, {int(pos[1])})")

    def add_test_gates(self):
        """Добавляет тестовые вентили (теперь пусто)"""
        # Оставляем поле пустым для чистого старта
        logging.debug("Поле очищено от тестовых вентилей")

    def pin_clicked(self, pin):
        """Метод который будут вызывать пины при клике"""
        logging.debug(f"Клик по пину: {pin.pin_type} на {pin.parent_gate.gate.name}")

        if self.selected_pin is None:
            self.selected_pin = pin
            logging.info(f"Выбран пин: {pin.parent_gate.gate.name} ({pin.pin_type})")

        else:
            first_pin = self.selected_pin
            second_pin = pin

            if first_pin.is_output() and second_pin.is_input():
                start_pin = first_pin
                end_pin = second_pin
            elif first_pin.is_input() and second_pin.is_output():
                start_pin = second_pin
                end_pin = first_pin
            else:
                logging.warning("Невозможно соединить два входа или два выхода")
                self.selected_pin = None
                return

            # ВАЖНО: проверяем, не существует ли уже такого соединения
            wire_exists = False
            for wire in start_pin.connected_wires:
                if wire.start_pin == start_pin and wire.end_pin == end_pin:
                    wire_exists = True
                    break

            if wire_exists:
                logging.warning("Соединение уже существует!")
                self.selected_pin = None
                return

            logging.info(f"Создание провода: {start_pin.parent_gate.gate.name} -> {end_pin.parent_gate.gate.name}")
            self.create_wire(start_pin, end_pin)
            self.selected_pin = None

    def create_wire(self, start_pin, end_pin):
        """Создает провод между двумя пинами"""
        logging.info(f"Создание провода: {start_pin.parent_gate.gate.name} -> {end_pin.parent_gate.gate.name}")

        wire = WireGraphicsItem(start_pin, end_pin)
        self.scene.addItem(wire)

        logging.debug("Провод создан")

        # ЗАКОММЕНТИРУЙ эту строку - симуляция уже запускается в connect_gates
        # self.simulate_circuit()

        # Только итоговое состояние для дебага
        if logging.getLogger().isEnabledFor(logging.DEBUG):
            states = []
            for item in self.scene.items():
                if hasattr(item, 'gate'):
                    states.append(f"{item.gate.name}:{item.gate.get_output()}")
            logging.debug("Состояния: " + " | ".join(states))



    def clear_scene(self):
        """Очищает всю сцену от всех элементов, кроме сетки"""
        reply = QMessageBox.question(
            self,
            'Подтверждение очистки',
            'Вы уверены, что хотите очистить поле?\nВсе вентили и соединения будут удалены.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Удаляем только пользовательские элементы (вентили и провода)
            # Оставляем сетку и фон

            items_to_remove = []
            for item in self.scene.items():
                # Проверяем тип элемента
                if (hasattr(item, 'gate') or  # Все вентили
                        isinstance(item, WireGraphicsItem) or  # Все провода
                        (hasattr(item, 'parent_gate') and hasattr(item, 'pin_type'))):  # Все пины
                    items_to_remove.append(item)

            # Удаляем найденные элементы
            for item in items_to_remove:
                self.scene.removeItem(item)

            # Сбрасываем состояние
            self.selected_pin = None

            # Логируем действие
            logging.info(f"Удалено {len(items_to_remove)} элементов со сцены")

            # Обновляем таблицу истинности
            self.truth_table.table.clear()
            self.truth_table.table.setRowCount(0)
            self.truth_table.table.setColumnCount(0)

            # Запускаем симуляцию для обновления состояния
            self.simulate_circuit()

    def simulate_with_inputs(self, input_values):
        """Устанавливает входы, симулирует схему и возвращает значения всех вентилей"""
        logging.debug(f"simulate_with_inputs: входные значения {input_values}")

        # Находим все Input вентили
        input_gates = []
        for item in self.scene.items():
            if hasattr(item, 'gate') and item.gate.name == "INPUT":
                input_gates.append(item)

        if len(input_gates) != len(input_values):
            logging.warning(
                f"Количество Input вентилей ({len(input_gates)}) не совпадает с количеством входных значений ({len(input_values)})")
            return {}

        # Сохраняем оригинальные значения входов
        original_inputs = [gate.gate.get_output() for gate in input_gates]

        # Устанавливаем новые значения
        for i, gate_item in enumerate(input_gates):
            gate_item.gate.set_value(input_values[i])

        # Сбрасываем все вентили
        for item in self.scene.items():
            if hasattr(item, 'gate'):
                item.gate.reset_computation()

        # Симулируем схему (один проход достаточно)
        self.update_all_connections()

        # Вычисляем выходы
        for item in self.scene.items():
            if hasattr(item, 'gate'):
                # Принудительно вычисляем выход
                item.gate.get_output()

        # Собираем результаты
        results = {}
        for item in self.scene.items():
            if hasattr(item, 'gate'):
                results[id(item.gate)] = item.gate.get_output()

        # Восстанавливаем оригинальные значения
        for i, gate_item in enumerate(input_gates):
            gate_item.gate.set_value(original_inputs[i])

        # Снова сбрасываем для восстановления состояния
        for item in self.scene.items():
            if hasattr(item, 'gate'):
                item.gate.reset_computation()

        return results

    def create_main_toolbar(self):
        """Создает верхний тулбар с кнопками управления"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)

        # Кнопка симуляции
        btn_simulate = QAction("▶️ Simulate", self)
        btn_simulate.triggered.connect(self.simulate_circuit)
        toolbar.addAction(btn_simulate)

        toolbar.addSeparator()

        # Кнопки для установки значений
        btn_set_0 = QAction("Set Input to 0", self)
        btn_set_0.triggered.connect(lambda: self.set_selected_input(0))
        toolbar.addAction(btn_set_0)

        btn_set_1 = QAction("Set Input to 1", self)
        btn_set_1.triggered.connect(lambda: self.set_selected_input(1))
        toolbar.addAction(btn_set_1)

    def simulate_circuit(self):
        """Запускает симуляцию всей схемы"""
        logging.debug("=" * 50)
        logging.debug("НАЧАЛО ДЕТАЛЬНОЙ СИМУЛЯЦИИ")
        logging.debug("=" * 50)
        # 1. Собираем информацию о всех вентилях
        all_gates = []
        # main_window.py - ДОБАВИТЬ в simulate_circuit() в начале

        logging.debug("=" * 50)
        logging.debug("НАЧАЛО СИМУЛЯЦИИ")
        # Выводим состояние всех вентилей перед симуляцией
        for item in self.scene.items():
            if hasattr(item, 'gate'):
                gate = item.gate
                inputs_str = str(gate.inputs) if hasattr(gate, 'inputs') else "нет"
                logging.debug(f"  {gate.name}: inputs={inputs_str}, output={gate.output}")

        logging.debug(f"Все вентили на сцене: {all_gates}")


        # 1. Сбрасываем ВСЕ вычисления
        for item in self.scene.items():
            if hasattr(item, 'gate'):
                item.gate.reset_computation()

        # 2. ОБНОВЛЯЕМ ВСЕ СОЕДИНЕНИЯ
        self.update_all_connections()

        # 3. ВЫЧИСЛЯЕМ МНОГО РАЗ чтобы гарантировать распространение
        final_states = {}
        for pass_num in range(5):  # 5 проходов для надежности
            any_changed = False

            for item in self.scene.items():
                if hasattr(item, 'gate'):
                    old_output = item.gate.output
                    new_output = item.gate.get_output()

                    if old_output != new_output:
                        any_changed = True
                        if logging.getLogger().isEnabledFor(logging.DEBUG):
                            logging.debug(f"Проход {pass_num + 1}: {item.gate.name} {old_output}->{new_output}")

                    final_states[item.gate.name] = new_output

            # Если на этом проходе ничего не изменилось - выходим
            if not any_changed:
                if pass_num > 0 and logging.getLogger().isEnabledFor(logging.DEBUG):
                    logging.debug(f"Схема стабилизировалась за {pass_num + 1} проходов")
                break

        # 4. Перерисовываем сцену
        self.scene.update()

        # Только итоговый результат
        if logging.getLogger().isEnabledFor(logging.INFO):
            states_str = ", ".join([f"{name}:{state}" for name, state in final_states.items()])
            logging.info(f"Результат симуляции: {states_str}")

    def topological_sort(self):
        """Сортирует вентили в порядке вычислений (Input -> ... -> Output)"""
        gates = [item for item in self.scene.items() if hasattr(item, 'gate')]

        # Простой подход: несколько проходов пока все не вычислятся
        sorted_gates = []
        remaining_gates = gates.copy()

        max_passes = 10  # Защита от бесконечного цикла
        for pass_num in range(max_passes):
            if not remaining_gates:
                break

            ready_gates = []
            for gate_item in remaining_gates:
                # Input gates всегда готовы
                if gate_item.gate.name == "INPUT":
                    ready_gates.append(gate_item)
                    continue

                # Проверяем зависят ли входы от других gates
                inputs_ready = True
                for pin in gate_item.input_pins:
                    for wire in pin.connected_wires:
                        start_gate = wire.start_pin.parent_gate
                        if start_gate in remaining_gates:
                            inputs_ready = False
                            break

                if inputs_ready:
                    ready_gates.append(gate_item)

            # Убираем готовые gates из оставшихся
            for gate in ready_gates:
                if gate in remaining_gates:
                    remaining_gates.remove(gate)
                    sorted_gates.append(gate)

        # Добавляем оставшиеся gates в конце
        sorted_gates.extend(remaining_gates)

        if logging.getLogger().isEnabledFor(logging.DEBUG):
            order = [g.gate.name for g in sorted_gates]
            logging.debug(f"Порядок вычислений: {order}")

        return sorted_gates

    # main_window.py - ЗАМЕНА метода update_all_connections()

    def update_all_connections(self):
        """Обновляет все логические соединения в схеме - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        logging.debug("Обновление всех соединений схемы")

        # 1. Сбрасываем inputs у всех вентилей (кроме InputGate)
        for item in self.scene.items():
            if hasattr(item, 'gate') and hasattr(item.gate, 'inputs'):
                if item.gate.name != "INPUT":
                    # Полностью очищаем inputs
                    item.gate.inputs = []

        # 2. Устанавливаем соединения через провода
        count = 0
        for item in self.scene.items():
            if isinstance(item, WireGraphicsItem):
                item.connect_gates()
                count += 1

        logging.debug(f"Обновлено {count} соединений")

    def set_selected_input(self, value):
        """Устанавливает значение выбранному Input элементу"""
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            if isinstance(item, InputGateGraphicsItem):
                item.gate.set_value(value)
                logging.info(f"Input установлен в: {value}")
                item.update()  # Перерисовываем

    def keyPressEvent(self, event):
        selected_items = self.scene.selectedItems()

        for item in selected_items:
            if isinstance(item, InputGateGraphicsItem):
                if event.key() == Qt.Key.Key_0:
                    item.gate.set_value(0)
                    logging.info("Input установлен в 0")
                elif event.key() == Qt.Key.Key_1:
                    item.gate.set_value(1)
                    logging.info("Input установлен в 1")

                # ПРИНУДИТЕЛЬНОЕ ОБНОВЛЕНИЕ
                logging.debug("Обновление схемы после изменения Input")
                self.update_all_connections()
                self.simulate_circuit()

        self.scene.update()

    def update_all_connections(self):
        """Обновляет все логические соединения в схеме"""
        logging.debug("Обновление всех соединений схемы")
        count = 0
        for item in self.scene.items():
            if isinstance(item, WireGraphicsItem):
                item.connect_gates()
                count += 1
        logging.debug(f"Обновлено {count} соединений")