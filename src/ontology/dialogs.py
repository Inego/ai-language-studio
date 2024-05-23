import json
import random
import re
from typing import List, Dict

from ontology.Age import Age
from ontology.Gender import Gender
from ontology.Locale import Locale
from state.Dialog import DialogCreationAlgorithm


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

    def generate_initial_prompt(self, locale: Locale, algorithm: DialogCreationAlgorithm) -> DialogPreliminary:
        main_interlocutor = self.random_interlocutor()
        other_interlocutor = self.random_interlocutor()

        main_type = main_interlocutor.name
        other_type = other_interlocutor.name

        main_gender = main_interlocutor.gender
        main_name = locale.pick_random_name(main_gender)
        other_gender = other_interlocutor.gender
        other_name = locale.pick_random_name(other_gender, [main_name])

        main_description = random.choice(main_interlocutor.descriptions)
        other_relation = random.choice(main_interlocutor.other[other_type])

        if algorithm == DialogCreationAlgorithm.PARTICIPANTS_AND_SPEC:
            prompt_start = (f"Suggest a creative context for a dialog in {locale.locale_name} between {main_name}, a {main_description}, "
                            f'and {other_relation} {other_name}.')

        elif algorithm == DialogCreationAlgorithm.WORD_CARDS:
            prompt_start = (f"Suggest a creative context for a dialog in {locale.locale_name} between {main_name} ({main_gender.value}) "
                            f'and {other_name} ({other_gender.value}).')

        else:
            raise Exception("Shoot")

        prompt_end = (f'Output the result in the following format:\n'
                      f'# Context\n'
                      f'<context>\n'
                      f'# Dialog\n'
                      f'{main_name}:\n'
                      f'{other_name}:\n'
                      f'...')

        if locale.special_note:
            prompt_start = prompt_start + ". " + locale.special_note

        assigned_voice_map = locale.assign_voices(
            [
                (main_name, main_gender),
                (other_name, other_gender)
            ]
        )

        return DialogPreliminary(
            prompt_start,
            prompt_end,
            [
                [main_type, main_name, main_gender.to_char(), assigned_voice_map[main_name]],
                [other_type, other_name, other_gender.to_char(), assigned_voice_map[other_name]],
            ])

    def random_interlocutor(self) -> InterlocutorDefinition:
        selected_key = random.choice(self.weighted_keys)
        return self.interlocutors[selected_key]


def do_main():
    dialogs = Dialogs.parse_from_json_file("../../data/dialogs.json")
    locale_name = "tr"
    locale = Locale.parse_from_file_name(f"../../data/{locale_name}.json")

    initial_prompt = dialogs.generate_initial_prompt(locale, DialogCreationAlgorithm.PARTICIPANTS_AND_SPEC)
    print(initial_prompt)


def extract_context_and_dialog(input_string):

    # Use regex to find the anchors at the start of lines
    context_match = re.search(r'^# Context\n', input_string, re.MULTILINE)
    dialog_match = re.search(r'^# Dialog\n', input_string, re.MULTILINE)

    # If either anchor is not found, return (None, None)
    if not context_match or not dialog_match:
        return None, None

    context_start = context_match.end()
    dialog_start = dialog_match.end()

    context = input_string[context_start:dialog_match.start()].strip()
    dialog = input_string[dialog_start:].strip()

    return context, dialog


if __name__ == '__main__':
    do_main()
