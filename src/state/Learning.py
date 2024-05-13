import json
from typing import List


from state.Dialog import Dialog
from state.Node import Node
from state.RootNode import RootNode
from state.WordCard import WordCard


class Learning:
    def __init__(self, language: str, second_language: str, root_node: Node, word_cards_focused: List[WordCard], word_cards_main: List[WordCard]):
        self.language = language
        self.second_language = second_language
        self.root_node = root_node
        self.word_cards_focused = word_cards_focused
        self.word_cards_main = word_cards_main

    @classmethod
    def from_data(cls, data):
        return cls(
            data["language"],
            data.get("secondLanguage", "en"),
            parse_node(data["root"]),
            [WordCard(x[0], x[1], x[2]) for x in data.get("wordCardsFocused", [])],
            [WordCard(x[0], x[1], x[2]) for x in data.get("wordCardsMain", [])]
        )

    @classmethod
    def from_json_file(cls, json_file_path):
        with open(json_file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
            return cls.from_data(json_data)

    def add_root_node(self, node: Node):
        self.root_node.add_child(node)
        self.root_node.child_index = len(self.root_node.nodes) - 1

    def save_to(self, filename):
        json_object = self.prepare_json_object()

        with open(filename, 'w', encoding='utf-8') as outfile:
            json.dump(json_object, outfile, indent=2, ensure_ascii=False)

    def prepare_json_object(self):
        return {
            "language": self.language,
            "secondLanguage": self.second_language,
            "root": self.root_node.prepare_json_object(),
            "wordCardsFocused": [[x.word, x.definition, x.translation] for x in self.word_cards_focused],
            "wordCardsMain": [[x.word, x.definition, x.translation] for x in self.word_cards_main]
        }


def parse_node(data) -> Node:
    node_type = data.get("type")
    if node_type == "dialog":
        result = Dialog.from_data(data)
    elif node_type is None:
        result = RootNode()
    else:
        raise Exception(f"Unknown node type: {node_type}")
    child_nodes = data.get("nodes")
    if child_nodes:
        for child in child_nodes:
            result.add_child(parse_node(child))
        result.child_index = data["childIndex"]
    return result


def do_main():
    learning = Learning.from_json_file("../../user-data/tr.json")
    learning.save_to("../../user-data/tr-saved.json")


if __name__ == '__main__':
    do_main()
