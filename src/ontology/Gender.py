from enum import Enum


class Gender(Enum):
    MALE = 'male'
    FEMALE = 'female'

    def to_char(self):
        if self == Gender.MALE:
            return 'm'
        elif self == Gender.FEMALE:
            return 'f'
        else:
            raise ValueError(f"Invalid gender: {self}")

    @classmethod
    def from_char(cls, gender_char):
        if gender_char == 'm':
            return cls.MALE
        elif gender_char == 'f':
            return cls.FEMALE
        else:
            raise ValueError(f"Invalid gender character: {gender_char}")
