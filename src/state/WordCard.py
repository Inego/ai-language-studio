from typing import List


class WordCard:
    def __init__(self, identifier: str, word: str, word_comment: str, translation: str, translation_comment: str):
        self.identifier = identifier
        self.word = word
        self.word_comment = word_comment
        self.translation = translation
        self.translation_comment = translation_comment

    @classmethod
    def from_list(cls, data: list):
        if len(data) != 5:
            raise ValueError("List must contain exactly 5 elements")
        return cls(data[0], data[1], data[2], data[3], data[4])

    def to_list(self):
        return [self.identifier, self.word, self.word_comment, self.translation, self.translation_comment]


class WordCardCollection:
    def __init__(self, focused: List[WordCard], main: List[WordCard]):
        self.focused = focused
        self.main = main
