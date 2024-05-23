import logging
import os
import sys
import traceback

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QDialog, QMainWindow, \
    QAction
from dotenv import load_dotenv
from openai import OpenAI

from ontology.Locale import Locale
from ontology.dialogs import Dialogs
from service.AudioPlayer import AudioPlayer
from service.SaveService import SaveServiceThread
from state.Dialog import Dialog
from state.Learning import Learning
from state.WordCard import move_id_to_end
from ui.widgets.LanguageDialogBlock import LanguageDialogWidget
from ui.widgets.NodeWidget import UiContext
from ui.widgets.modal.WordCardsDialog import WordCardsDialog
from ui.widgets.modal.GenerateDialogModal import GenerateDialogModal
from ui.widgets.widget_utils import clear_layout

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def log_uncaught_exceptions(ex_cls, ex, tb):
    text = ''.join(traceback.format_exception(ex_cls, ex, tb))
    logging.critical(f'Uncaught exception:\n{text}')


sys.excepthook = log_uncaught_exceptions


class MainWindow(QMainWindow):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.learning = Learning.from_json_file(file_path)
        self.save_service = SaveServiceThread()
        self.save_service.start()
        self.save_service.connect(self.save_learning)

        self.dialogs = Dialogs.parse_from_json_file("../../data/dialogs.json")

        locale_name = self.learning.language
        self.locale = Locale.parse_from_file_name(f"../../data/{locale_name}.json")

        second_locale_name = self.learning.second_language
        self.second_locale = Locale.parse_from_file_name(f"../../data/{second_locale_name}.json")

        self.openai_client = OpenAI()
        self.audio_player = AudioPlayer(self.openai_client, self)

        self.setWindowTitle("AI Language Studio")

        # Create main menu
        main_menu = self.menuBar()
        file_menu = main_menu.addMenu('File')

        # Add actions to the file menu
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        word_cards_action = QAction('Word Cards', self)
        word_cards_action.triggered.connect(self.open_word_cards)
        file_menu.addAction(word_cards_action)

        main_layout = QVBoxLayout()

        create_dialog_button = QPushButton("Create Dialog")
        create_dialog_button.clicked.connect(self.create_dialog)
        main_layout.addWidget(create_dialog_button)

        self.dynamic_layout = QVBoxLayout()
        main_layout.addLayout(self.dynamic_layout)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.build_from_node_path()

    def create_dialog(self):
        self.open_generate_dialog_modal()

    def open_generate_dialog_modal(self):
        dialog = GenerateDialogModal(
            self.openai_client, self.dialogs, self.locale, self.second_locale, self.learning.create_dialog_settings,
            self.learning.word_cards_focused + self.learning.word_cards_main,
            parent=self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            dialog = dialog.result
            self.learning.add_root_node(dialog)

            for identifier in dialog.selected_word_card_ids:
                move_id_to_end(self.learning.word_cards_focused, identifier)
                move_id_to_end(self.learning.word_cards_main, identifier)

            self.save_and_rebuild()

    def open_word_cards(self):
        dialog = WordCardsDialog(self, self.learning.word_cards_focused, self.learning.word_cards_main)
        if dialog.exec_() == QDialog.Accepted:
            word_cards_focused, word_cards_main = dialog.export_word_cards()
            self.learning.word_cards_focused = word_cards_focused
            self.learning.word_cards_main = word_cards_main
            self.trigger_save()

    def save_learning(self):
        print("Saving learning...")
        self.learning.save_to(self.file_path)

    def save_and_rebuild(self):
        self.trigger_save()
        self.build_from_node_path()

    def build_from_node_path(self):

        clear_layout(self.dynamic_layout)

        node_creation_context = UiContext(self.audio_player, self.trigger_save, self.save_and_rebuild, self.learning)

        learning = self.learning
        current_node = learning.root_node
        while current_node.nodes:
            current_node = current_node.nodes[current_node.child_index]
            widget = self.create_widget(current_node, node_creation_context)
            self.dynamic_layout.addWidget(widget)

    def create_widget(self, current_node, node_creation_context: UiContext):
        if isinstance(current_node, Dialog):
            return LanguageDialogWidget(current_node, node_creation_context)

    def trigger_save(self):
        self.save_service.trigger_save()

    def closeEvent(self, event):
        if self.save_service.pending_save():
            self.save_learning()


def do_main(file_path):
    load_dotenv()
    try:
        q_app = QApplication(sys.argv)
        main_window = MainWindow(file_path)
        main_window.show()
        sys.exit(q_app.exec_())
    except SystemExit as e:
        raise e
    except:
        logging.exception("Exception in main()")


if __name__ == '__main__':
    print("Current directory:", os.getcwd())
    if len(sys.argv) < 2:
        print("Usage: python main.py <file_path>")
        sys.exit(1)
    do_main(sys.argv[1])
