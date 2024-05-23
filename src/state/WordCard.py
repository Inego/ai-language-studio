from typing import List, Callable


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

    def __repr__(self):
        return (f"WordCard(identifier={self.identifier!r}, word={self.word!r}, "
                f"word_comment={self.word_comment!r}, translation={self.translation!r}, "
                f"translation_comment={self.translation_comment!r})")


def move_card(cards: List[WordCard], identifier: str, position_func: Callable[[List[WordCard], WordCard], None]):
    index = next((i for i, card in enumerate(cards) if card.identifier == identifier), None)
    if index is not None:
        card = cards.pop(index)
        position_func(cards, card)


def move_id_to_end(cards: List[WordCard], identifier: str):
    move_card(cards, identifier, lambda cs, c: cs.append(c))


def move_id_to_start(cards: List[WordCard], identifier: str):
    move_card(cards, identifier, lambda cs, c: cs.insert(0, c))


def pop_card(cards: List[WordCard], identifier: str):
    index = next((i for i, card in enumerate(cards) if card.identifier == identifier), None)
    if index is not None:
        card = cards.pop(index)
        return card
    return None
