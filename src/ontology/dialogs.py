import json
import random
from typing import List, Dict

from ontology.Age import Age
from ontology.Gender import Gender
from ontology.Locale import Locale


class InterlocutorDefinition:
    def __init__(self, name: str, gender: Gender, age: Age, descriptions: List[str], other: Dict[str, List[str]]):
        self.name = name
        self.gender = gender
        self.age = age
        self.descriptions = descriptions
        self.other = other


class DialogPreliminary:
    def __init__(self, prompt_start: str, prompt_end: str, interlocutors: list[list]):
        self.prompt = prompt_start
        self.prompt_end = prompt_end
        self.interlocutors = interlocutors


class Dialogs:
    def __init__(self, interlocutors: Dict[str, InterlocutorDefinition]):
        self.interlocutors = interlocutors
        self.interlocutor_key_list = list(self.interlocutors.keys())

        self.weighted_keys = []
        for key in self.interlocutor_key_list:
            interlocutor = self.interlocutors[key]
            # Adults are twice as likely to be picked compared to children
            weight = 2 if interlocutor.age == Age.ADULT else 1
            self.weighted_keys.extend([key] * weight)

    @classmethod
    def parse_from_json_data(cls, json_data):
        interlocutors = dict()
        for interlocutor_name, interlocutor_data in json_data['interlocutors'].items():
            gender = Gender(interlocutor_data['gender'])
            age = Age(interlocutor_data['age'])
            descriptions = interlocutor_data['descriptions']
            other = interlocutor_data['other']
            interlocutor = InterlocutorDefinition(interlocutor_name, gender, age, descriptions, other)
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

        main_type = main_interlocutor.name
        other_type = other_interlocutor.name

        main_name = locale.pick_random_name(main_interlocutor.gender)
        other_name = locale.pick_random_name(other_interlocutor.gender, [main_name])

        main_description = random.choice(main_interlocutor.descriptions)
        other_relation = random.choice(main_interlocutor.other[other_type])

        prompt_start = (f"Write a dialog between {main_name}, a {main_description}, "
                  f'and {other_relation} {other_name}.')

        prompt_end = (f'The dialog is in {locale.locale_name}. '
                      f'Start each utterance with the name only ("{main_name}:", "{other_name}:").')

        if locale.special_note:
            prompt_start = prompt_start + ". " + locale.special_note

        assigned_voice_map = locale.assign_voices(
            [
                (main_name, main_interlocutor.gender),
                (other_name, other_interlocutor.gender)
            ]
        )

        return DialogPreliminary(
            prompt_start,
            prompt_end,
            [
                [main_type, main_name, main_interlocutor.gender.to_char(), assigned_voice_map[main_name]],
                [other_type, other_name, other_interlocutor.gender.to_char(), assigned_voice_map[other_name]],
            ])

    def random_interlocutor(self) -> InterlocutorDefinition:
        selected_key = random.choice(self.weighted_keys)
        return self.interlocutors[selected_key]


def do_main():
    dialogs = Dialogs.parse_from_json_file("../../data/dialogs.json")
    locale_name = "tr"
    locale = Locale.parse_from_file_name(f"../../data/{locale_name}.json")

    initial_prompt = dialogs.generate_initial_prompt(locale)
    print(initial_prompt)


if __name__ == '__main__':
    do_main()
