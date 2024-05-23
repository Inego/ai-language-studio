from typing import List, Tuple

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, \
    QLineEdit, QPushButton, QMessageBox

from state.WordCard import WordCard
from utils import my_random, time_utils


class WordCardTableRow:
    def __init__(self, word_card: WordCard, focused: bool):
        self.word_card = word_card
        self.focused = focused


def convert_to_word_card_table_rows(word_cards_focused: List[WordCard], word_cards_main: List[WordCard]):
    return ([WordCardTableRow(word_card, True) for word_card in word_cards_focused] +
            [WordCardTableRow(word_card, False) for word_card in word_cards_main])





class WordCardsDialog(QDialog):
    def __init__(self, parent, word_cards_focused, word_cards_main):
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
        add_panel_layout.addWidget(QLabel("Word Comment:"))
        self.word_comment_line_edit = QLineEdit()
        add_panel_layout.addWidget(self.word_comment_line_edit)
        add_panel_layout.addWidget(QLabel("Translation:"))
        self.translation_line_edit = QLineEdit()
        add_panel_layout.addWidget(self.translation_line_edit)
        add_panel_layout.addWidget(QLabel("Translation Comment:"))
        self.translation_comment_line_edit = QLineEdit()
        add_panel_layout.addWidget(self.translation_comment_line_edit)
        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.add_word_card)
        add_panel_layout.addWidget(self.add_button)
        layout.addLayout(add_panel_layout)

        # Table widget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(["Word", "Word Comment", "Translation", "Translation Comment"])
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

        self.table_rows = convert_to_word_card_table_rows(word_cards_focused, word_cards_main)
        self.populate_table(self.table_rows)

        self.center_on_parent()

        self.words_added = False

    def export_word_cards(self) -> Tuple[List[WordCard], List[WordCard]]:
        focused_cards = []
        main_cards = []
        for row in self.table_rows:
            (focused_cards if row.focused else main_cards).append(row.word_card)
        return focused_cards, main_cards

    def populate_table(self, word_card_table_rows):
        self.table_widget.setRowCount(len(word_card_table_rows))
        for row, table_row in enumerate(word_card_table_rows):
            card = table_row.word_card
            self.table_widget.setItem(row, 0, QTableWidgetItem(card.word))
            self.table_widget.setItem(row, 1, QTableWidgetItem(card.word_comment))
            self.table_widget.setItem(row, 2, QTableWidgetItem(card.translation))
            self.table_widget.setItem(row, 3, QTableWidgetItem(card.translation_comment))

    def center_on_parent(self):
        parent_geometry = self.parent().frameGeometry()
        screen_center = parent_geometry.center()
        dialog_rect = self.frameGeometry()
        dialog_rect.moveCenter(screen_center)
        self.move(dialog_rect.topLeft())

    def add_word_card(self):
        word = self.word_line_edit.text()
        word_comment = self.word_comment_line_edit.text()
        translation = self.translation_line_edit.text()
        translation_comment = self.translation_comment_line_edit.text()
        if word and translation:
            # Add in the table
            row = 0
            self.table_widget.insertRow(row)
            self.table_widget.setItem(row, 0, QTableWidgetItem(word))
            self.table_widget.setItem(row, 1, QTableWidgetItem(word_comment))
            self.table_widget.setItem(row, 2, QTableWidgetItem(translation))
            self.table_widget.setItem(row, 3, QTableWidgetItem(translation_comment))

            # Add to the backing collection
            self.table_rows.insert(0,
                                   WordCardTableRow(
                                       WordCard(time_utils.encode_by_time(), word, word_comment, translation, translation_comment), False))

            # Clear the edit fields
            self.word_line_edit.clear()
            self.word_comment_line_edit.clear()
            self.translation_line_edit.clear()
            self.translation_comment_line_edit.clear()
            self.word_line_edit.setFocus()
            self.words_added = True

    def on_cancel_clicked(self):
        if self.words_added:
            reply = QMessageBox.question(
                self, 'Confirm', "Really close and lose the changes?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.reject()
        else:
            self.reject()
