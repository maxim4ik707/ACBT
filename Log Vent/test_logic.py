import logging
from logic_gates import AndGate, OrGate, NotGate, InputGate, OutputGate

# Настраиваем логирование для тестов
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('circuit_simulator.log', mode='w')
    ]
)


def test_gates():
    logging.info("Testing logic gates...")

    # ТЕСТ 1: Базовые операции с явной установкой inputs
    logging.info("=== Базовые тесты ===")

    # AND
    and_gate = AndGate()
    and_gate.inputs = [1, 1]  # Явная установка
    result = and_gate.get_output()
    logging.info(f"AND(1, 1) = {result}")  # Ожидаем: 1
    assert result == 1, f"AND(1, 1) expected 1, got {result}"

    and_gate.inputs = [1, 0]
    result = and_gate.get_output()
    logging.info(f"AND(1, 0) = {result}")  # Ожидаем: 0
    assert result == 0, f"AND(1, 0) expected 0, got {result}"

    # OR
    or_gate = OrGate()
    or_gate.inputs = [0, 1]
    result = or_gate.get_output()
    logging.info(f"OR(0, 1) = {result}")  # Ожидаем: 1
    assert result == 1, f"OR(0, 1) expected 1, got {result}"

    or_gate.inputs = [0, 0]
    result = or_gate.get_output()
    logging.info(f"OR(0, 0) = {result}")  # Ожидаем: 0
    assert result == 0, f"OR(0, 0) expected 0, got {result}"

    # NOT
    not_gate = NotGate()
    not_gate.inputs = [1]
    result = not_gate.get_output()
    logging.info(f"NOT(1) = {result}")  # Ожидаем: 0
    assert result == 0, f"NOT(1) expected 0, got {result}"

    not_gate.inputs = [0]
    result = not_gate.get_output()
    logging.info(f"NOT(0) = {result}")  # Ожидаем: 1
    assert result == 1, f"NOT(0) expected 1, got {result}"

    # ТЕСТ 2: Соединение вентилей между собой
    logging.info("=== Тесты соединений ===")

    input1 = InputGate(1)
    input2 = InputGate(0)

    # AND с подключенными входами
    and_connected = AndGate()
    and_connected.inputs = [input1, input2]  # Подключаем другие вентили!
    result = and_connected.get_output()
    logging.info(f"AND(INPUT(1), INPUT(0)) = {result}")  # Ожидаем: 0
    assert result == 0, f"AND with connected inputs expected 0, got {result}"

    # NOT с подключенным AND
    not_connected = NotGate()
    not_connected.inputs = [and_connected]
    result = not_connected.get_output()
    logging.info(f"NOT(AND(1, 0)) = {result}")  # Ожидаем: 1
    assert result == 1, f"NOT(AND) expected 1, got {result}"

    logging.info("Все тесты пройдены успешно! ✅")


if __name__ == "__main__":
    test_gates()