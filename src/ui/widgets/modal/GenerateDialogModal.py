import json
from typing import Optional

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QStackedWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QWidget
from openai import OpenAI

from ontology.Locale import Locale
from ontology.dialogs import Dialogs
from state.Dialog import Dialog
from utils.openai_utils import stream_chat_completion, MODEL_BASIC


class GenerateDialogModal(QDialog):
    def __init__(self, openai_client: OpenAI, dialogs: Dialogs, locale: Locale, parent=None):
        super(GenerateDialogModal, self).__init__(parent)
        self.locale = locale
        self.dialogs = dialogs
        self.openai_client = openai_client
        self.result: Optional[Dialog] = None
        self.setWindowTitle('Generate Dialog')

        self.stacked_widget = QStackedWidget(self)

        self.first_panel = QDialog()
        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate)
        first_panel_layout = QVBoxLayout(self.first_panel)
        first_panel_layout.addWidget(self.generate_button)
        self.stacked_widget.addWidget(self.first_panel)

        self.second_panel = QDialog()
        self.second_panel_layout = QVBoxLayout(self.second_panel)
        self.second_panel_layout.addWidget(QLabel("Second Panel", self))
        self.stacked_widget.addWidget(self.second_panel)

        layout = QVBoxLayout(self)
        layout.addWidget(self.stacked_widget)

        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.cancel_button)

        self.setLayout(layout)

        self.current_counter_widget = None

    def add_stage_name(self, stage_name: str):

        stage_panel = QWidget(self)

        stage_layout = QHBoxLayout(stage_panel)

        stage_layout.addWidget(QLabel(stage_name, self))
        self.current_counter_widget = QLabel("...", self)
        stage_layout.addWidget(self.current_counter_widget)

        self.second_panel_layout.addWidget(stage_panel)

    def add_stage_current_count(self, current_count: int):
        self.current_counter_widget.setText(str(current_count))

    def finished(self, dialog: Dialog):
        self.result = dialog
        self.accept()

    def generate(self):
        self.stacked_widget.setCurrentIndex(1)

        thread = GenerateDialogThread(self.openai_client, self.dialogs, self.locale, self)
        thread.new_stage_signal.connect(self.add_stage_name)
        thread.update_count_signal.connect(self.add_stage_current_count)
        thread.finished_signal.connect(self.finished)
        thread.start()


class GenerateDialogThread(QThread):
    new_stage_signal = pyqtSignal(str)
    update_count_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(Dialog)

    def __init__(self, openai_client: OpenAI, dialogs: Dialogs, locale: Locale, parent=None):
        super(GenerateDialogThread, self).__init__(parent)
        self.locale = locale
        self.dialogs = dialogs
        self.openai_client = openai_client

    def run(self):
        language_name = self.locale.locale_name
        self.new_stage_signal.emit(f"Generating dialog in {language_name}")

        initial_prompt = self.dialogs.generate_initial_prompt(self.locale)

        dialog_orig = stream_chat_completion(
            self.openai_client,
            MODEL_BASIC,
            [{"role": "user", "content": initial_prompt.prompt}],
            1,
            lambda x: self.update_count_signal.emit(x)
        )

        print(dialog_orig)

        self.new_stage_signal.emit("Translating and packing to JSON")

        aligned = stream_chat_completion(
            self.openai_client,
            MODEL_BASIC,
            [{
                "role": "user",
                "content": f"Given the following dialog in {language_name}:"
                           f'\n```\n{dialog_orig}\n```\n'
                           f'generate a JSON list of each sentence with its English translation in the following format: '
                           f'`[[<who>, <{language_name}>, <English>], ...]`.'
            }],
            0,
            lambda x: self.update_count_signal.emit(x)
        )

        print(aligned)

        content = json.loads(aligned)
        result = Dialog.from_data({
            "interlocutors": initial_prompt.interlocutors,
            "currentPosition": 0,
            "content": content
        })
        self.finished_signal.emit(result)
