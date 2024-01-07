from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QPushButton, QHBoxLayout, QTextEdit, QSizePolicy

from languages.serbian import latin_to_cyrillic
from state.Dialog import Dialog
from ui.widgets.NodeWidget import NodeWidget, UiContext


class LanguageDialogWidget(NodeWidget):
    def __init__(self, dialog: Dialog, ui_context: UiContext):
        super().__init__(dialog, ui_context)

        self.dialog = dialog

        # Create labels and add them to the left layout
        self.label_who = QLabel("<...>")
        self.text_edit_src = QTextEdit()
        self.text_edit_src.setReadOnly(True)
        self.label_translation = QLabel("")
        self.show_level = 0
        self.navigate()

        self.main_layout.addWidget(self.label_who)
        self.main_layout.addWidget(self.text_edit_src)
        self.main_layout.addWidget(self.label_translation)

        # Set the main layout for the widget
        self.setLayout(self.main_layout)

        # Add control buttons
        self.add_controls()

        self.setFocusPolicy(Qt.StrongFocus)

    def add_controls(self):
        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()

        # Create buttons
        self.button_previous = QPushButton("<")
        self.button_next = QPushButton(">")
        button_play = QPushButton("Play")
        button_show = QPushButton("Show")

        self.button_previous.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.button_next.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_play.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_show.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Connect buttons to corresponding slots/methods
        self.button_previous.clicked.connect(self.navigate_previous)
        self.button_next.clicked.connect(self.navigate_next)
        button_play.clicked.connect(self.play_dialog)
        button_show.clicked.connect(self.reveal)

        # Add buttons to the button layout
        button_layout.addWidget(self.button_previous)
        button_layout.addWidget(self.button_next)
        button_layout.addWidget(button_play)
        button_layout.addWidget(button_show)
        button_layout.addStretch(1)  # Add stretch after buttons

        self.update_navigation_enabled()

        # Add the button layout to the main layout
        self.layout().addLayout(button_layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.navigate_previous()
        elif event.key() == Qt.Key_Right:
            self.navigate_next()

    def navigate(self, hide=False):
        if hide:
            self.show_level = 0
            self.ui_context.trigger_save()

            self.update_navigation_enabled()

            if self.dialog.dialog_type == "listen":
                self.play_dialog()

        sentence = self.get_current_sentence()
        self.label_who.setText(sentence.who)
        self.text_edit_src.setHtml(self.determine_main_text(sentence))
        self.label_translation.setText(self.determine_second_text(sentence))

    def determine_main_text(self, sentence):
        if self.dialog.dialog_type == "listen":
            return "..." if self.show_level == 0 else sentence.sentence
        elif self.dialog.dialog_type == "speak":
            return sentence.translation

        raise ValueError(f"Can't determine main text for {self.dialog.dialog_type}")

    def determine_second_text(self, sentence):
        if self.dialog.dialog_type == "listen":
            return "..." if self.show_level < 2 else sentence.translation
        elif self.dialog.dialog_type == "speak":
            return "..." if self.show_level < 1 else sentence.sentence
        raise ValueError(f"Can't determine second text for {self.dialog.dialog_type}")

    def update_navigation_enabled(self):
        self.button_previous.setEnabled(self.dialog.current_position > 0)
        self.button_next.setEnabled(self.dialog.current_position < len(self.dialog.content) - 1)

    def get_current_sentence(self):
        current_position = self.dialog.current_position
        sentence = self.dialog.content[current_position]
        return sentence

    def navigate_previous(self):
        if self.dialog.navigate(-1):
            self.navigate(True)

    def navigate_next(self):
        if self.dialog.navigate(1):
            self.navigate(True)

    def play_dialog(self):
        sentence = self.get_current_sentence()
        # Get corresponding interlocutor voice from the Dialog
        interlocutor = self.dialog.get_interlocutor(sentence.who)
        text_to_play = sentence.sentence
        if self.ui_context.learning.language == 'sr':
            text_to_play = latin_to_cyrillic(text_to_play)
        self.ui_context.audio_player.play(interlocutor.voice, text_to_play)

    def get_max_show_level(self):
        if self.dialog.dialog_type == "listen":
            return 2
        elif self.dialog.dialog_type == "speak":
            return 1
        raise ValueError(f"Can't get max show level for {self.dialog.dialog_type}")

    def reveal(self):
        if self.show_level < 2:
            self.show_level += 1
            self.navigate()
