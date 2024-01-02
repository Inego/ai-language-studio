import os
import sys

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QDialog, QHBoxLayout
from dotenv import load_dotenv
from openai import OpenAI

from ontology.Locale import Locale
from ontology.dialogs import Dialogs
from service.AudioPlayer import AudioPlayer
from service.SaveService import SaveServiceThread
from state.Dialog import Dialog
from state.Learning import Learning
from ui.widgets.ListeningDialogBlock import ListeningDialogBlock
from ui.widgets.NodeWidget import UiContext
from ui.widgets.modal.GenerateDialogModal import GenerateDialogModal
from ui.widgets.widget_utils import clear_layout


class MainWindow(QWidget):
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

        self.openai_client = OpenAI()
        self.audio_player = AudioPlayer(self.openai_client, self)

        self.setWindowTitle("AI Language Studio")

        main_layout = QVBoxLayout(self)

        button_layout = QHBoxLayout()

        button_show = QPushButton("Create dialog")
        button_show.clicked.connect(self.open_generate_dialog_modal)
        button_layout.addWidget(button_show)

        # Add the horizontal layout with the buttons to the main layout
        main_layout.addLayout(button_layout)

        self.dynamic_layout = QVBoxLayout()
        main_layout.addLayout(self.dynamic_layout)

        self.build_from_node_path()

    def open_generate_dialog_modal(self):
        dialog = GenerateDialogModal(self.openai_client, self.dialogs, self.locale, parent=self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            dialog = dialog.result
            self.learning.add_root_node(dialog)
            self.save_and_rebuild()

    def save_learning(self):
        print("Saving learning...")
        self.learning.save_to(self.file_path)

    def save_and_rebuild(self):
        self.trigger_save()
        self.build_from_node_path()

    def build_from_node_path(self):

        clear_layout(self.dynamic_layout)

        node_creation_context = UiContext(self.audio_player, self.trigger_save, self.save_and_rebuild)

        learning = self.learning
        current_node = learning.root_node
        while current_node.nodes:
            current_node = current_node.nodes[current_node.child_index]
            widget = self.create_widget(current_node, node_creation_context)
            self.dynamic_layout.addWidget(widget)

    def create_widget(self, current_node, node_creation_context: UiContext):
        if isinstance(current_node, Dialog):
            return ListeningDialogBlock(current_node, node_creation_context)

    def trigger_save(self):
        self.save_service.trigger_save()

    def closeEvent(self, event):
        if self.save_service.pending_save():
            self.save_learning()


def do_main(file_path):
    load_dotenv()
    q_app = QApplication(sys.argv)
    main_window = MainWindow(file_path)
    main_window.show()
    sys.exit(q_app.exec_())


if __name__ == '__main__':
    print("Current directory:", os.getcwd())
    if len(sys.argv) < 2:
        print("Usage: python main.py <file_path>")
        sys.exit(1)
    do_main(sys.argv[1])
