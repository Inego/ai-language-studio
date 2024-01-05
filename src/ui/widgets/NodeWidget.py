from abc import abstractmethod

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSizePolicy

from service.AudioPlayer import AudioPlayer
from state.Learning import Learning
from state.Node import Node


class UiContext:
    def __init__(self, audio_player: AudioPlayer, trigger_save, tree_navigation_callback, learning: Learning):
        self.audio_player = audio_player
        self.trigger_save = trigger_save
        self.tree_navigation_callback = tree_navigation_callback
        self.learning = learning


class NodeWidget(QWidget):
    tree_navigation_signal = pyqtSignal()

    def __init__(self, node: Node, ui_context: UiContext):
        super().__init__()
        self.node = node
        self.ui_context = ui_context
        self.tree_navigation_signal.connect(ui_context.tree_navigation_callback)
        self.main_layout = QVBoxLayout()

        # Create the horizontal layout
        h_layout = QHBoxLayout()

        # Create the "<" button
        left_button = QPushButton("<")
        left_button.clicked.connect(self.tree_navigate_left)

        if node.is_first_parents_child():
            left_button.setEnabled(False)

        # Create the "Dialog" label
        dialog_label = QLabel("Dialog")
        dialog_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # Set size policy to expanding
        dialog_label.setAlignment(Qt.AlignCenter)

        # Create the ">" button
        right_button = QPushButton(">")
        right_button.clicked.connect(self.tree_navigate_right)

        if node.is_last_parents_child():
            right_button.setEnabled(False)

        # Add the widgets to the horizontal layout with stretch factors
        h_layout.addWidget(left_button)
        h_layout.addWidget(dialog_label, 1)  # The stretch factor of 1 will make the label expand
        h_layout.addWidget(right_button)

        # Add the horizontal layout to the main layout with stretch
        self.main_layout.addLayout(h_layout, 1)  # The stretch factor of 1 will make the horizontal layout expand

        # Set the main layout as the layout for this widget
        self.setLayout(self.main_layout)

    def tree_navigate_left(self):
        self.tree_navigate(-1)

    def tree_navigate_right(self):
        self.tree_navigate(1)

    def tree_navigate(self, delta):
        self.node.parent.tree_navigate(delta)
        self.tree_navigation_signal.emit()

    @abstractmethod
    def add_controls(self):
        pass
