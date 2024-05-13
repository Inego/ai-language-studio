from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, \
    QLineEdit, QPushButton, QMessageBox

from state.WordCard import WordCard


class WordCardsDialog(QDialog):
    def __init__(self, parent, word_cards):
        super().__init__(parent)
        self.setWindowTitle("Word Cards")
        self.setModal(True)
        self.setGeometry(0, 0, 800, 400)

        layout = QVBoxLayout()

        # Panel for adding new word card
        add_panel_layout = QHBoxLayout()
        add_panel_layout.addWidget(QLabel("Word:"))
        self.word_line_edit = QLineEdit()
        add_panel_layout.addWidget(self.word_line_edit)
        add_panel_layout.addWidget(QLabel("Translation:"))
        self.translation_line_edit = QLineEdit()
        add_panel_layout.addWidget(self.translation_line_edit)
        add_panel_layout.addWidget(QLabel("Definition:"))
        self.definition_line_edit = QLineEdit()
        add_panel_layout.addWidget(self.definition_line_edit)
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_word_card)
        add_panel_layout.addWidget(self.add_button)
        layout.addLayout(add_panel_layout)

        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(3)
        self.table_widget.setHorizontalHeaderLabels(["Word", "Translation", "Definition"])
        layout.addWidget(self.table_widget)

        # OK and Cancel buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.populate_table(word_cards)

        self.center_on_parent()

        self.word_cards = word_cards
        self.words_added = False

    def populate_table(self, word_cards):
        self.table_widget.setRowCount(len(word_cards))
        for row, card in enumerate(word_cards):
            self.table_widget.setItem(row, 0, QTableWidgetItem(card.word))
            self.table_widget.setItem(row, 1, QTableWidgetItem(card.translation))
            self.table_widget.setItem(row, 2, QTableWidgetItem(card.definition))

    def center_on_parent(self):
        parent_geometry = self.parent().frameGeometry()
        screen_center = parent_geometry.center()
        dialog_rect = self.frameGeometry()
        dialog_rect.moveCenter(screen_center)
        self.move(dialog_rect.topLeft())

    def add_word_card(self):
        word = self.word_line_edit.text()
        translation = self.translation_line_edit.text()
        definition = self.definition_line_edit.text()
        if word and translation:
            self.table_widget.insertRow(0)
            self.table_widget.setItem(0, 0, QTableWidgetItem(word))
            self.table_widget.setItem(0, 1, QTableWidgetItem(translation))
            self.table_widget.setItem(0, 2, QTableWidgetItem(definition))
            self.word_line_edit.clear()
            self.translation_line_edit.clear()
            self.definition_line_edit.clear()
            self.word_line_edit.setFocus()
            self.words_added = True

    def collect_data(self):
        self.word_cards = []
        for row in range(self.table_widget.rowCount()):
            word = self.table_widget.item(row, 0).text()
            translation = self.table_widget.item(row, 1).text()
            definition = self.table_widget.item(row, 2).text() if self.table_widget.item(row, 2) else ""
            self.word_cards.append(WordCard(word, translation, definition))

    def accept(self):
        self.collect_data()
        super().accept()

    def on_cancel_clicked(self):
        if self.words_added:
            reply = QMessageBox.question(
                self, 'Confirm', "Really close and lose the changes?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.reject()
        else:
            self.reject()

    def get_word_cards(self):
        return self.word_cards
