import json
from typing import Optional, List

from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QDialog, QStackedWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QWidget, QCheckBox, \
    QTextEdit, QRadioButton, QButtonGroup
from openai import OpenAI

from ontology.Locale import Locale
from ontology.dialogs import Dialogs, DialogPreliminary, extract_context_and_dialog
from state.Dialog import Dialog, CreateDialogSettings, DialogCreationAlgorithm, DialogType
from state.WordCard import WordCard
from utils.my_random import select_and_remove
from utils.openai_utils import stream_chat_completion, MODEL_BASIC, MODEL_HEAVY


class GenerateDialogModal(QDialog):
    def __init__(self, openai_client: OpenAI, dialogs: Dialogs, locale: Locale, second_locale: Locale,
                 settings: CreateDialogSettings, word_cards_combined: List[WordCard], parent=None):
        super(GenerateDialogModal, self).__init__(parent)
        self.locale = locale
        self.second_locale = second_locale
        self.settings = settings
        self.word_cards_combined = word_cards_combined
        self.dialogs = dialogs
        self.openai_client = openai_client
        self.result: Optional[Dialog] = None
        self.setWindowTitle('Generate Dialog')

        self.initial_prompt = self.generate_initial_prompt()

        self.stacked_widget = QStackedWidget(self)

        self.first_panel = self.create_first_panel()
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

    def create_first_panel(self):
        first_panel = QWidget(self)
        first_panel_layout = QVBoxLayout(first_panel)

        dialog_controls_layout = self.create_create_dialog_controls()
        first_panel_layout.addLayout(dialog_controls_layout)

        self.first_panel_stacked_widget = QStackedWidget(self)
        first_panel_layout.addWidget(self.first_panel_stacked_widget)

        self.create_participants_and_spec_panel()
        self.create_word_cards_panel()

        self.generate_button = QPushButton("Generate")
        self.generate_button.clicked.connect(self.generate)
        first_panel_layout.addWidget(self.generate_button)

        return first_panel

    def create_participants_and_spec_panel(self):
        self.participants_and_spec_panel = QWidget()
        participants_and_spec_panel_layout = QVBoxLayout(self.participants_and_spec_panel)

        self.plot_details_edit = QTextEdit()
        participants_and_spec_panel_layout.addWidget(self.plot_details_edit)


        self.first_panel_stacked_widget.addWidget(self.participants_and_spec_panel)

    def create_word_cards_panel(self):
        self.word_cards_panel = QWidget()
        word_cards_panel_layout = QVBoxLayout(self.word_cards_panel)
        word_cards_label = QLabel("Word Cards", self.word_cards_panel)
        word_cards_panel_layout.addWidget(word_cards_label)

        self.first_panel_stacked_widget.addWidget(self.word_cards_panel)

    def switch_panel(self, index):
        self.first_panel_stacked_widget.setCurrentIndex(index)

    def create_create_dialog_controls(self):
        settings = self.settings

        dialog_controls_rows = QVBoxLayout()

        dialog_controls_first_row = QHBoxLayout()

        dialog_type_layout = QVBoxLayout()
        self.radio_dialog_type_listen = QRadioButton("Listen")
        self.radio_dialog_type_speak = QRadioButton("Speak")
        dialog_type_group = QButtonGroup(self)
        dialog_type_group.addButton(self.radio_dialog_type_listen)
        dialog_type_group.addButton(self.radio_dialog_type_speak)
        dialog_type_layout.addWidget(self.radio_dialog_type_listen)
        dialog_type_layout.addWidget(self.radio_dialog_type_speak)

        if settings.dialog_type == DialogType.LISTEN:
            self.radio_dialog_type_listen.setChecked(True)
        else:
            self.radio_dialog_type_speak.setChecked(True)

        self.radio_dialog_type_listen.toggled.connect(lambda: self.update_dialog_type(DialogType.LISTEN))
        self.radio_dialog_type_speak.toggled.connect(lambda: self.update_dialog_type(DialogType.SPEAK))

        algo_layout = QVBoxLayout()
        self.radio_algo_participant = QRadioButton("By participants and spec")
        self.radio_algo_word_cards = QRadioButton("With word cards")
        algo_group = QButtonGroup(self)
        algo_group.addButton(self.radio_algo_participant)
        algo_group.addButton(self.radio_algo_word_cards)
        algo_layout.addWidget(self.radio_algo_participant)
        algo_layout.addWidget(self.radio_algo_word_cards)

        if settings.algorithm == DialogCreationAlgorithm.PARTICIPANTS_AND_SPEC:
            self.radio_algo_participant.setChecked(True)
        else:
            self.radio_algo_word_cards.setChecked(True)

        self.radio_algo_participant.toggled.connect(
            lambda: self.update_algorithm(DialogCreationAlgorithm.PARTICIPANTS_AND_SPEC))
        self.radio_algo_word_cards.toggled.connect(lambda: self.update_algorithm(DialogCreationAlgorithm.WORD_CARDS))

        self.use_heavy_model_checkbox = QCheckBox("Use heavy model")
        self.use_heavy_model_checkbox.setChecked(settings.use_heavy_model)
        self.use_heavy_model_checkbox.stateChanged.connect(self.update_use_heavy_model)

        dialog_controls_first_row.addLayout(dialog_type_layout)
        dialog_controls_first_row.addLayout(algo_layout)
        dialog_controls_first_row.addWidget(self.use_heavy_model_checkbox)

        dialog_controls_rows.addLayout(dialog_controls_first_row)

        plot_row = QHBoxLayout()
        regen_button = QPushButton("\U0001F501", self)
        regen_button.clicked.connect(self.regen_plot)
        plot_row.addWidget(regen_button)
        self.plot_label = QLabel("Plot", self)
        plot_row.addWidget(self.plot_label)
        self.refresh_plot_label()

        dialog_controls_rows.addLayout(plot_row)

        return dialog_controls_rows

    def update_dialog_type(self, dialog_type):
        self.settings.dialog_type = dialog_type

    def update_algorithm(self, algorithm):
        self.settings.algorithm = algorithm
        if algorithm == DialogCreationAlgorithm.PARTICIPANTS_AND_SPEC:
            self.switch_panel(0)
        elif algorithm == DialogCreationAlgorithm.WORD_CARDS:
            self.switch_panel(1)
        self.regen_plot()

    def update_use_heavy_model(self, state):
        self.settings.use_heavy_model = (state == Qt.Checked)

    def regen_plot(self):
        self.initial_prompt = self.generate_initial_prompt()
        self.refresh_plot_label()

    def generate_initial_prompt(self):
        return self.dialogs.generate_initial_prompt(self.locale, self.settings.algorithm)

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
            self.settings,
            self.initial_prompt,
            self.plot_details_edit.toPlainText(),
            self.word_cards_combined,
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
                 settings: CreateDialogSettings,
                 initial_prompt: DialogPreliminary,
                 prompt_details: str,
                 word_cards_combined: List[WordCard],
                 parent=None):
        super(GenerateDialogThread, self).__init__(parent)
        self.openai_client = openai_client
        self.dialogs = dialogs
        self.locale = locale
        self.second_locale = second_locale
        self.settings = settings
        self.initial_prompt = initial_prompt
        self.prompt_details = prompt_details
        self.word_cards_combined = word_cards_combined

    def run(self):
        language_name = self.locale.locale_name
        second_language_name = self.second_locale.locale_name
        self.new_stage_signal.emit(f"Generating dialog in {language_name}")

        prompt = self.initial_prompt.prompt

        selected_word_card_ids = []
        if self.settings.algorithm == DialogCreationAlgorithm.PARTICIPANTS_AND_SPEC:
            if self.prompt_details:
                prompt += " " + self.prompt_details

        elif self.settings.algorithm == DialogCreationAlgorithm.WORD_CARDS:
            # Retrieve 3 weighted
            selected_words: List[WordCard] = select_and_remove(self.word_cards_combined, 3)
            if selected_words:
                prompt += (" The dialog should feature the following words: " +
                           ", ".join(f'"{w.word}"' for w in selected_words) + ".")
            selected_word_card_ids = [w.identifier for w in selected_words]

        prompt += " " + self.initial_prompt.prompt_end
        print(prompt)
        dialog_orig = stream_chat_completion(
            self.openai_client,
            MODEL_HEAVY if self.locale.heavy_generation or self.settings.use_heavy_model else MODEL_BASIC,
            [{"role": "user", "content": prompt}],
            1,
            lambda x: self.update_count_signal.emit(x)
        )
        print(dialog_orig)

        context_text, dialog_text = extract_context_and_dialog(dialog_orig)

        self.new_stage_signal.emit("Translating and packing to JSON")
        aligned = stream_chat_completion(
            self.openai_client,
            MODEL_BASIC,
            [{
                "role": "user",
                "content": f"{context_text}\n"
                           f"Given their dialog in {language_name}:"
                           f'\n```\n{dialog_text}\n```\n'
                           f'output a JSON list of each utterance from this dialog with its {second_language_name} translation in the following format: '
                           f'`[[<who>, <{language_name} utterance>, <{second_language_name} translation>], ...]`. Do not use Markdown!'
            }],
            0,
            lambda x: self.update_count_signal.emit(x)
        )
        print(aligned)
        content = json.loads(aligned)
        result = Dialog.from_data({
            "dialogType": self.settings.dialog_type,
            "interlocutors": self.initial_prompt.interlocutors,
            "currentPosition": 0,
            "content": content,
            "context": context_text,
            "selectedWordCardIds": selected_word_card_ids
        })

        self.finished_signal.emit(result)
