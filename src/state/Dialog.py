from dataclasses import dataclass
from enum import Enum

from state.Node import Node


class Interlocutor:
    def __init__(self, type, name, gender, voice):
        self.type = type
        self.name = name
        self.gender = gender
        self.voice = voice


class Sentence:
    def __init__(self, who, sentence, translation):
        self.who = who
        self.sentence = sentence
        self.translation = translation


class Dialog(Node):
    def prepare_specific_json_object(self):
        return {
            "type": "dialog",
            "dialogType": self.dialog_type,
            "interlocutors": [[i.type, i.name, i.gender, i.voice] for i in self.interlocutors],
            "currentPosition": self.current_position,
            "content": [[s.who, s.sentence, s.translation] for s in self.content]
        }

    def __init__(self, dialog_type: str, interlocutors: list[Interlocutor], current_position, content: list[Sentence]):
        super().__init__()
        self.dialog_type = dialog_type
        self.interlocutors = interlocutors
        self.current_position = current_position
        self.content = content

    @classmethod
    def from_data(cls, data):
        interlocutors = [Interlocutor(*interlocutor) for interlocutor in data['interlocutors']]
        content = [Sentence(*sentence) for sentence in data['content']]
        return cls(data.get("dialogType", "speak"), interlocutors, data['currentPosition'], content)

    def navigate(self, delta):
        new_current_position = self.current_position + delta
        if 0 <= new_current_position < len(self.content):
            self.current_position = new_current_position
            return True
        return False

    def get_interlocutor(self, who):
        for interlocutor in self.interlocutors:
            if interlocutor.name == who:
                return interlocutor
        return None


class DialogType(Enum):
    LISTEN = "listen"
    SPEAK = "speak"


class DialogCreationAlgorithm(Enum):
    PARTICIPANTS_AND_SPEC = "participants_and_spec"
    WORD_CARDS = "word_cards"


@dataclass
class CreateDialogSettings:
    dialog_type: DialogType = DialogType.LISTEN  # Default value
    algorithm: DialogCreationAlgorithm = DialogCreationAlgorithm.PARTICIPANTS_AND_SPEC  # Default value
    use_heavy_model: bool = False  # Default value

    def to_data(self) -> dict:
        # Custom serialization to handle enums
        return {
            "dialog_type": self.dialog_type.value,
            "algorithm": self.algorithm.value,
            "use_heavy_model": self.use_heavy_model
        }

    @staticmethod
    def from_data(data: dict):
        return CreateDialogSettings(
            dialog_type=DialogType(data.get('dialog_type', DialogType.LISTEN.value)),
            algorithm=DialogCreationAlgorithm(data.get('algorithm', DialogCreationAlgorithm.PARTICIPANTS_AND_SPEC.value)),
            use_heavy_model=data.get('use_heavy_model', False)
        )
