import json
from typing import Optional

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QDialog, QStackedWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QWidget, QCheckBox, \
    QTextEdit
from openai import OpenAI

from ontology.Locale import Locale
from ontology.dialogs import Dialogs, DialogPreliminary
from state.Dialog import Dialog
from utils.openai_utils import stream_chat_completion, MODEL_BASIC, MODEL_HEAVY


class GenerateDialogModal(QDialog):
    def __init__(self, openai_client: OpenAI, dialogs: Dialogs, locale: Locale, second_locale: Locale, dialog_type: str, parent=None):
        super(GenerateDialogModal, self).__init__(parent)
        self.locale = locale
        self.second_locale = second_locale
        self.dialog_type = dialog_type
        self.dialogs = dialogs
        self.openai_client = openai_client
        self.result: Optional[Dialog] = None
        self.setWindowTitle(f'Generate Dialog ({dialog_type})')
        self.initial_prompt = self.generate_initial_prompt()

        self.stacked_widget = QStackedWidget(self)

        self.first_panel = QDialog()
        first_panel_layout = QVBoxLayout(self.first_panel)

        # Create a horizontal layout for the reload button and plot label
        plot_layout = QHBoxLayout()

        # Create the reload button with the unicode symbol for the reload icon
        regen_button = QPushButton("\U0001F501", self)
        regen_button.clicked.connect(self.regen_plot)
        plot_layout.addWidget(regen_button)

        # Create the label with the text "plot"
        self.plot_label = QLabel("Plot", self)
        plot_layout.addWidget(self.plot_label)

        self.refresh_plot_label()

        # Add the horizontal layout to the first panel layout
        first_panel_layout.addLayout(plot_layout)

        self.plot_details_edit = QTextEdit()
        first_panel_layout.addWidget(self.plot_details_edit)

        self.heavy_model_checkbox = QCheckBox("Heavy model", self)
        first_panel_layout.addWidget(self.heavy_model_checkbox)  # Add the checkbox to the layout

        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate)
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

    def regen_plot(self):
        self.initial_prompt = self.generate_initial_prompt()
        self.refresh_plot_label()

    def generate_initial_prompt(self):
        return self.dialogs.generate_initial_prompt(self.locale)

    def refresh_plot_label(self):
        self.plot_label.setText(self.initial_prompt.prompt)

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

        thread = GenerateDialogThread(
            self.openai_client,
            self.dialogs,
            self.locale,
            self.second_locale,
            self.dialog_type,
            self.heavy_model_checkbox.isChecked(),
            self.initial_prompt,
            self.plot_details_edit.toPlainText(),
            self
        )
        thread.new_stage_signal.connect(self.add_stage_name)
        thread.update_count_signal.connect(self.add_stage_current_count)
        thread.finished_signal.connect(self.finished)
        thread.start()


class GenerateDialogThread(QThread):
    new_stage_signal = pyqtSignal(str)
    update_count_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(Dialog)

    def __init__(self,
                 openai_client: OpenAI,
                 dialogs: Dialogs,
                 locale: Locale,
                 second_locale: Locale,
                 dialog_type: str,
                 use_heavy_model: bool,
                 initial_prompt: DialogPreliminary,
                 prompt_details: str,
                 parent=None):
        super(GenerateDialogThread, self).__init__(parent)
        self.openai_client = openai_client
        self.dialogs = dialogs
        self.locale = locale
        self.second_locale = second_locale
        self.dialog_type = dialog_type
        self.use_heavy_model = use_heavy_model
        self.initial_prompt = initial_prompt
        self.prompt_details = prompt_details

    def run(self):
        language_name = self.locale.locale_name
        second_language_name = self.second_locale.locale_name
        self.new_stage_signal.emit(f"Generating dialog in {language_name}")

        prompt = self.initial_prompt.prompt
        if self.prompt_details:
            prompt += " " + self.prompt_details
        prompt += " " + self.initial_prompt.prompt_end

        print(prompt)

        dialog_orig = stream_chat_completion(
            self.openai_client,
            MODEL_HEAVY if self.locale.heavy_generation or self.use_heavy_model else MODEL_BASIC,
            [{"role": "user", "content": prompt}],
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
                           f'output a JSON list of each utterance from this dialog with its {second_language_name} translation in the following format: '
                           f'`[[<who>, <{language_name} utterance>, <{second_language_name} translation>], ...]`. Do not use Markdown!'
            }],
            0,
            lambda x: self.update_count_signal.emit(x)
        )

        print(aligned)

        content = json.loads(aligned)
        result = Dialog.from_data({
            "dialogType": self.dialog_type,
            "interlocutors": self.initial_prompt.interlocutors,
            "currentPosition": 0,
            "content": content
        })
        self.finished_signal.emit(result)
