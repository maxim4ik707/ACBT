import sys
import traceback
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from PyQt6.QtGui import QColor

def except_hook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print("КРИТИЧЕСКАЯ ОШИБКА:")
    print(tb)

    # Записываем в лог
    with open("crash.log", "w") as f:
        f.write(tb)

    sys.exit(1)


sys.excepthook = except_hook


# main.py - ЗАМЕНЯЕМ функцию main()

def main():
    app = QApplication(sys.argv)

    # Устанавливаем стиль Fusion для современного вида
    app.setStyle("Fusion")

    # Устанавливаем цветовую палитру
    palette = app.palette()
    palette.setColor(app.palette().ColorRole.Window, QColor(240, 240, 240))
    palette.setColor(app.palette().ColorRole.WindowText, QColor(0, 0, 0))
    palette.setColor(app.palette().ColorRole.Base, QColor(255, 255, 255))
    palette.setColor(app.palette().ColorRole.AlternateBase, QColor(245, 245, 245))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()