from typing import Dict, Any

from state.Node import Node


class RootNode(Node):
    def prepare_specific_json_object(self) -> Dict[str, Any]:
        return {}

    def __init__(self):
        super().__init__()
