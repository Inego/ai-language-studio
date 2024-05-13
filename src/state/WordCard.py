from typing import List


class WordCard:
    def __init__(self, word: str, translation: str, definition: str):
        self.word = word
        self.translation = translation
        self.definition = definition


class WordCardCollection:
    def __init__(self, focused: List[WordCard], main: List[WordCard]):
        self.focused = focused
        self.main = main
