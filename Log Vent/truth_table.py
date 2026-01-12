from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,\
    QLabel, QPushButton, QHBoxLayout, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import copy
import logging


class TruthTableWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.input_gates = []
        self.other_gates = []
        self.output_gates = []
        self.gate_order = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Верхняя панель с кнопкой
        top_panel = QHBoxLayout()
        self.title_label = QLabel("Таблица истинности схемы:")
        top_panel.addWidget(self.title_label)
        top_panel.addStretch()

        # truth_table.py - ОБНОВЛЯЕМ init_ui()

        self.update_button = QPushButton("📊 Анализировать схему")
        self.update_button.setFixedHeight(35)  # Увеличиваем высоту
        self.update_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                padding: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.update_button.clicked.connect(self.analyze_and_update_table)
        top_panel.addWidget(self.update_button)

        layout.addLayout(top_panel)

        # Таблица
        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)

    def collect_gates_from_scene(self):
        """Собирает вентили со сцены и определяет порядок"""
        self.input_gates = []
        self.other_gates = []
        self.output_gates = []
        self.gate_order = []

        if not self.main_window.scene:
            logging.warning("Нет сцены для анализа")
            return

        # Собираем все вентили
        all_gates = []
        for item in self.main_window.scene.items():
            if hasattr(item, 'gate'):
                all_gates.append(item)

        if not all_gates:
            logging.warning("На сцене нет вентилей")
            return

        # Сортируем по позиции X (слева направо)
        all_gates.sort(key=lambda x: x.pos().x())

        # Распределяем по категориям
        for gate_item in all_gates:
            gate = gate_item.gate
            if gate.name == "INPUT":
                self.input_gates.append(gate_item)
            elif gate.name == "OUTPUT":
                self.output_gates.append(gate_item)
            else:
                self.other_gates.append(gate_item)

        # Порядок: Input -> Другие вентили -> Output
        self.gate_order = self.input_gates + self.other_gates + self.output_gates

        logging.info(
            f"Найдено вентилей: {len(self.gate_order)} (Input: {len(self.input_gates)}, Other: {len(self.other_gates)}, Output: {len(self.output_gates)})")

    # truth_table.py - ЗАМЕНЯЕМ метод generate_all_input_combinations()

    def generate_all_input_combinations(self):
        """Генерирует все комбинации значений для Input вентилей в порядке возрастания"""
        if not self.input_gates:
            return []

        num_inputs = len(self.input_gates)
        combinations = []

        # Генерируем от 0 до 2^n - 1
        for i in range(2 ** num_inputs):
            combo = []
            # Преобразуем число в бинарный список, начиная с младшего бита
            for bit in range(num_inputs - 1, -1, -1):
                value = (i >> bit) & 1
                combo.append(value)
            combinations.append(combo)

        logging.debug(f"Сгенерировано {len(combinations)} комбинаций в порядке возрастания")
        return combinations


    # truth_table.py - ЗАМЕНЯЕМ метод setup_table_style()
    def setup_table_style(self):
        """Настраивает стиль таблицы"""
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setGridStyle(Qt.PenStyle.SolidLine)

        # Устанавливаем режим растяжения заголовков
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)  # Автоподбор по содержимому
        header.setStretchLastSection(False)  # Запрещаем растяжение последней колонки

        # Устанавливаем минимальные и максимальные ширины
        header.setMinimumSectionSize(50)
        header.setMaximumSectionSize(150)

        # Устанавливаем высоту строк
        for i in range(self.table.rowCount()):
            self.table.setRowHeight(i, 30)

        # Настраиваем стиль ячеек для лучшей читаемости
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #cccccc;
                gridline-color: #e0e0e0;
                font-family: "Segoe UI", Arial;
                font-size: 11pt;
            }

            QTableWidget::item {
                padding: 5px;
                border: none;
                color: #333333;  /* Темно-серый текст для контраста */
                font-weight: 500;
            }

            QTableWidget::item:selected {
                background-color: #4a86e8;
                color: white;
            }

            QHeaderView::section {
                background-color: #4a86e8;
                color: white;
                padding: 8px;
                border: none;
                font-weight: bold;
                font-size: 11pt;
            }
        """)


    # truth_table.py - ЗАМЕНА simulate_with_inputs() полностью
    def simulate_with_inputs(self, input_values):
        """Устанавливает значения Input и симулирует схему"""
        logging.debug(f"=== НАЧАЛО СИМУЛЯЦИИ с входами: {input_values} ===")

        # 1. Запоминаем оригинальные значения Input
        original_values = {}
        for i, gate_item in enumerate(self.input_gates):
            original_values[i] = gate_item.gate.get_output()

        # 2. Устанавливаем новые значения для Input
        for i, gate_item in enumerate(self.input_gates):
            if i < len(input_values):
                gate = gate_item.gate
                if hasattr(gate, 'set_value'):
                    gate.set_value(input_values[i])
                    logging.debug(f"Установлен Input {i}: {input_values[i]}")
                else:
                    logging.error(f"Input gate {i} не имеет set_value")

        # 3. ПРИНУДИТЕЛЬНО сбрасываем ВСЕ вычисления
        for gate_item in self.gate_order:
            gate_item.gate.reset_computation()

        # 4. Запускаем симуляцию через main_window (чтобы все соединения обновились)
        if self.main_window:
            self.main_window.update_all_connections()
            self.main_window.simulate_circuit()

        # 5. Собираем конечные значения
        gate_values = {}
        for gate_item in self.gate_order:
            gate = gate_item.gate
            value = gate.get_output()
            gate_values[id(gate)] = value
            logging.debug(f"Итоговое значение {gate.name}: {value}")

        # 6. Восстанавливаем оригинальные значения
        for i, gate_item in enumerate(self.input_gates):
            if i in original_values:
                gate = gate_item.gate
                if hasattr(gate, 'set_value'):
                    gate.set_value(original_values[i])

        # 7. Снова сбрасываем для восстановления состояния
        for gate_item in self.gate_order:
            gate_item.gate.reset_computation()

        logging.debug(f"=== КОНЕЦ СИМУЛЯЦИИ ===")
        return gate_values

    # truth_table.py - ЗАМЕНА метода analyze_and_update_table() полностью

    def analyze_and_update_table(self):
        """Анализирует схему и заполняет таблицу истинности - УПРОЩЕННАЯ ВЕРСИЯ"""
        logging.info("=" * 50)
        logging.info("НАЧИНАЕМ АНАЛИЗ СХЕМЫ")
        logging.info("=" * 50)

        # Собираем информацию о вентилях
        self.collect_gates_from_scene()

        # Проверяем наличие Input
        if not self.input_gates:
            logging.warning("Нет Input вентилей для анализа")
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        # Генерируем все комбинации входов
        input_combinations = self.generate_all_input_combinations()
        logging.info(f"Генерируем {len(input_combinations)} комбинаций входов")

        # Настраиваем таблицу
        total_columns = len(self.gate_order)
        self.table.setColumnCount(total_columns)
        self.table.setRowCount(len(input_combinations))

        # Устанавливаем заголовки
        headers = []
        input_counter = 1
        output_counter = 1
        other_counter = {}

        for gate_item in self.gate_order:
            gate = gate_item.gate
            if gate.name == "INPUT":
                headers.append(f"Ин{input_counter}")
                input_counter += 1
            elif gate.name == "OUTPUT":
                headers.append(f"Вых{output_counter}")
                output_counter += 1
            else:
                if gate.name not in other_counter:
                    other_counter[gate.name] = 1
                else:
                    other_counter[gate.name] += 1
                headers.append(f"{gate.name}{other_counter[gate.name]}")

        self.table.setHorizontalHeaderLabels(headers)

        # Заполняем таблицу для каждой комбинации входов
        logging.info("Заполняем таблицу...")
        for row, input_combo in enumerate(input_combinations):
            logging.info(f"Комбинация {row + 1}/{len(input_combinations)}: {input_combo}")

            # Используем новый метод simulate_with_inputs для получения значений
            gate_values = self.main_window.simulate_with_inputs(input_combo)

            # Заполняем строку таблицы
            for col, gate_item in enumerate(self.gate_order):
                gate = gate_item.gate
                value = gate_values.get(id(gate), "?")

                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # Подсветка значений
                if value == 1:
                    item.setBackground(QColor(144, 238, 144))  # Светло-зеленый
                    item.setForeground(QColor(0, 100, 0))  # Темно-зеленый текст
                elif value == 0:
                    item.setBackground(QColor(255, 182, 193))  # Светло-красный
                    item.setForeground(QColor(139, 0, 0))  # Темно-красный текст
                else:
                    item.setBackground(QColor(255, 255, 150))  # Светло-желтый
                    item.setForeground(QColor(102, 102, 0))  # Темно-желтый текст

                # Устанавливаем жирный шрифт для значений
                font = item.font()
                font.setBold(True)
                font.setPointSize(11)
                item.setFont(font)

                self.table.setItem(row, col, item)

        # Автоподгонка и стиль
        self.table.resizeColumnsToContents()
        self.setup_table_style()

        logging.info("Таблица истинности обновлена!")

        # Выводим первые 3 строки для проверки
        logging.info("=" * 50)
        logging.info("РЕЗУЛЬТАТЫ ЗАПОЛНЕНИЯ ТАБЛИЦЫ:")
        for row in range(min(3, self.table.rowCount())):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "?")
            logging.info(f"Строка {row}: {row_data}")
        logging.info("=" * 50)