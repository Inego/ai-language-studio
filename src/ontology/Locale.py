import json
import random

from ontology.Gender import Gender


class Locale:
    def __init__(self, locale_name: str, male_names: list[str], female_names: list[str], male_voices: list[str], female_voices: list[str]):
        self.locale_name = locale_name
        self.male_names = male_names
        self.female_names = female_names
        self.male_voices = male_voices
        self.female_voices = female_voices

    def pick_random_name(self, gender, exclusions=None):
        if exclusions is None:
            exclusions = []
        base_list = self.male_names if gender == Gender.MALE else self.female_names
        available_names = [name for name in base_list if name not in exclusions]
        return random.choice(available_names)

    @staticmethod
    def parse_from_json_string(json_string):
        data = json.loads(json_string)
        locale_name = data['name']
        male_names = data['names']['male']
        female_names = data['names']['female']
        male_voices = data['voices']['male']
        female_voices = data['voices']['female']
        return Locale(locale_name, male_names, female_names, male_voices, female_voices)

    @staticmethod
    def parse_from_file_name(file_name):
        with open(file_name, 'r', encoding='utf=8') as file:
            return Locale.parse_from_json_string(file.read())

    def assign_voices_for_gender(self, names, gender: Gender):
        result = {}
        base_voices = self.male_voices if gender == Gender.MALE else self.female_voices
        current_voices = None
        for name in names:
            if not current_voices:
                current_voices = base_voices[:]
            voice = random.choice(current_voices)
            current_voices.remove(voice)
            result[name] = voice

        return result

    def assign_voices(self, interlocutors: list[tuple[str, Gender]]):
        # Gather two lists of male and female names
        male_names = [name for name, gender in interlocutors if gender == Gender.MALE]
        female_names = [name for name, gender in interlocutors if gender == Gender.FEMALE]
        male_voices = self.assign_voices_for_gender(male_names, Gender.MALE)
        female_voices = self.assign_voices_for_gender(female_names, Gender.FEMALE)
        # Return a merged map for all names
        return {**male_voices, **female_voices}
