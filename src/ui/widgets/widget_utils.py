from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLayout

large_qedit_font = QFont()
large_qedit_font.setPointSize(12)


def clear_layout(layout: QLayout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clear_layout(item.layout())
