import logging


class LogicGate:
    def __init__(self, name):
        self.name = name
        self.output = None
        self.inputs = []  # Список входных соединений (теперь объекты или значения)

    def compute_output(self):
        raise NotImplementedError("Subclasses must implement compute_output()")

    def reset_computation(self):
        self.output = None

    def get_output(self):
        if self.output is None:
            self.output = self.compute_output()
        return self.output

    def set_input(self, input_value):
        self.inputs.append(input_value)
        self.output = None


class AndGate(LogicGate):
    def __init__(self):
        super().__init__("AND")

    def compute_output(self):
        if not self.inputs:
            return 0

        values = []
        for inp in self.inputs:
            if hasattr(inp, 'get_output'):
                values.append(inp.get_output())
            else:
                values.append(inp)

        # Фильтруем только 0/1
        values = [v for v in values if v in (0, 1)]

        if len(values) < 2:
            return 0

        # AND: все входы должны быть 1
        return 1 if all(v == 1 for v in values) else 0


class OrGate(LogicGate):
    def __init__(self):
        super().__init__("OR")

    def compute_output(self):
        if not self.inputs:
            return 0

        values = []
        for inp in self.inputs:
            if hasattr(inp, 'get_output'):
                values.append(inp.get_output())
            else:
                values.append(inp)

        values = [v for v in values if v in (0, 1)]

        # OR: хотя бы один вход должен быть 1
        return 1 if any(v == 1 for v in values) else 0


class NotGate(LogicGate):
    def __init__(self):
        super().__init__("NOT")

    def compute_output(self):
        if not self.inputs:
            return 1  # NOT без входа = 1

        input_val = self.inputs[0]
        if hasattr(input_val, 'get_output'):
            input_val = input_val.get_output()

        # NOT: инвертирует вход
        return 0 if input_val == 1 else 1


class NandGate(LogicGate):
    def __init__(self):
        super().__init__("NAND")

    def compute_output(self):
        if not self.inputs:
            return 1

        values = []
        for inp in self.inputs:
            if hasattr(inp, 'get_output'):
                values.append(inp.get_output())
            else:
                values.append(inp)

        values = [v for v in values if v in (0, 1)]

        if len(values) < 2:
            return 1

        # NAND = NOT(AND)
        and_result = 1 if all(v == 1 for v in values) else 0
        return 0 if and_result == 1 else 1


class NorGate(LogicGate):
    def __init__(self):
        super().__init__("NOR")

    def compute_output(self):
        if not self.inputs:
            return 1

        values = []
        for inp in self.inputs:
            if hasattr(inp, 'get_output'):
                values.append(inp.get_output())
            else:
                values.append(inp)

        values = [v for v in values if v in (0, 1)]

        # NOR = NOT(OR)
        or_result = 1 if any(v == 1 for v in values) else 0
        return 0 if or_result == 1 else 1


class XorGate(LogicGate):
    def __init__(self):
        super().__init__("XOR")

    def compute_output(self):
        if not self.inputs:
            return 0

        values = []
        for inp in self.inputs:
            if hasattr(inp, 'get_output'):
                values.append(inp.get_output())
            else:
                values.append(inp)

        values = [v for v in values if v in (0, 1)]

        if len(values) < 2:
            return 0

        # XOR: нечетное количество единиц
        count_ones = sum(1 for v in values if v == 1)
        return 1 if count_ones % 2 == 1 else 0


class InputGate(LogicGate):
    def __init__(self, initial_value=0):
        super().__init__("INPUT")
        self.value = initial_value
        self.inputs = [initial_value]  # Для совместимости

    def compute_output(self):
        return self.value

    def set_value(self, value):
        self.value = value
        self.inputs[0] = value
        self.output = value


class OutputGate(LogicGate):
    def __init__(self):
        super().__init__("OUTPUT")
        self.inputs = []

    def compute_output(self):
        if not self.inputs:
            return 0

        input_val = self.inputs[0]
        if hasattr(input_val, 'get_output'):
            return input_val.get_output()
        else:
            return input_val

    def get_value(self):
        return self.get_output()