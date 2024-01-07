from state.Node import Node


class Interlocutor:
    def __init__(self, name, gender, voice):
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
            "interlocutors": [[i.name, i.gender, i.voice] for i in self.interlocutors],
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
