from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class Node(ABC):
    def __init__(self):
        self.nodes: List[Node] = []
        self.child_index = -1
        self.parent: Optional[Node] = None

    @abstractmethod
    def prepare_specific_json_object(self) -> Dict[str, Any]:
        """
        For saving/serializing, prepare the JSON object specific to the implementation of the Node.
        This method should be implemented by subclasses to define their own JSON structure.
        """
        pass

    def prepare_json_object(self) -> Dict[str, Any]:
        """
        Prepare the JSON object for the current node, including the JSON objects for its child nodes.
        """
        # Call the implementation-specific method to get the JSON object for the current node
        json_object = self.prepare_specific_json_object()

        if self.nodes:
            # Prepare the JSON objects for the child nodes and add them to the 'nodes' property
            json_object['nodes'] = [child.prepare_json_object() for child in self.nodes]
            json_object['childIndex'] = self.child_index

        return json_object

    def add_child(self, child: Node):
        self.nodes.append(child)
        child.child_index = len(self.nodes) - 1
        child.parent = self

    def is_first_parents_child(self):
        return self.parent.is_first_child(self)

    def is_last_parents_child(self):
        return self.parent.is_last_child(self)

    def is_first_child(self, child: Node):
        return self.nodes[0] == child

    def is_last_child(self, child: Node):
        return self.nodes[-1] == child

    def tree_navigate(self, delta):
        new_child_index = self.child_index + delta
        if new_child_index < 0:
            raise ValueError(f"new_child_index {new_child_index}")
        elif new_child_index >= len(self.nodes):
            raise ValueError(f"new_child_index {new_child_index} >= len(self.nodes) which is {len(self.nodes)}")
        self.child_index = new_child_index
