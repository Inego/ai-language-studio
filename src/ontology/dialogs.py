import json
import random
from typing import List, Dict

from ontology.Gender import Gender
from ontology.Locale import Locale


class InterlocutorDefinition:
    def __init__(self, name: str, gender: Gender, descriptions: List[str], other: Dict[str, List[str]]):
        self.name = name
        self.gender = gender
        self.descriptions = descriptions
        self.other = other


class DialogPreliminary:
    def __init__(self, prompt: str, interlocutors: list[list]):
        self.prompt = prompt
        self.interlocutors = interlocutors


class Dialogs:
    def __init__(self, interlocutors: Dict[str, InterlocutorDefinition]):
        self.interlocutors = interlocutors
        self.interlocutor_key_list = list(self.interlocutors.keys())

    @classmethod
    def parse_from_json_data(cls, json_data):
        interlocutors = dict()
        for interlocutor_name, interlocutor_data in json_data['interlocutors'].items():
            gender = Gender(interlocutor_data['gender'])
            descriptions = interlocutor_data['descriptions']
            other = interlocutor_data['other']
            interlocutor = InterlocutorDefinition(interlocutor_name, gender, descriptions, other)
            interlocutors[interlocutor_name] = interlocutor
        return Dialogs(interlocutors)

    @classmethod
    def parse_from_json_file(cls, json_file_name):
        with open(json_file_name, encoding="utf-8") as json_file:
            file_content = json.load(json_file)
            return cls.parse_from_json_data(file_content)

    def generate_initial_prompt(self, locale: Locale) -> DialogPreliminary:
        main_interlocutor = self.random_interlocutor()
        other_interlocutor = self.random_interlocutor()

        other_type = other_interlocutor.name

        main_name = locale.pick_random_name(main_interlocutor.gender)
        other_name = locale.pick_random_name(other_interlocutor.gender, [main_name])

        main_description = random.choice(main_interlocutor.descriptions)
        other_relation = random.choice(main_interlocutor.other[other_type])

        result = (f"Write a dialog in {locale.locale_name} between {main_name}, a {main_description}, "
                  f'and {other_relation} {other_name}. Start each utterance with the name only ("{main_name}:", "{other_name}:").')

        if locale.special_note:
            result = result + ". " + locale.special_note

        assigned_voice_map = locale.assign_voices(
            [
                (main_name, main_interlocutor.gender),
                (other_name, other_interlocutor.gender)
            ]
        )

        return DialogPreliminary(result, [
            [main_name, main_interlocutor.gender.to_char(), assigned_voice_map[main_name]],
            [other_name, other_interlocutor.gender.to_char(), assigned_voice_map[other_name]],
        ])

    def random_interlocutor(self) -> InterlocutorDefinition:
        interlocutor_key = random.choice(self.interlocutor_key_list)
        return self.interlocutors[interlocutor_key]


def do_main():
    dialogs = Dialogs.parse_from_json_file("../../data/dialogs.json")
    locale_name = "tr"
    locale = Locale.parse_from_file_name(f"../../data/{locale_name}.json")

    initial_prompt = dialogs.generate_initial_prompt(locale)
    print(initial_prompt)


if __name__ == '__main__':
    do_main()
