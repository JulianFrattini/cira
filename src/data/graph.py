from ast import List
from dataclasses import dataclass, field

from src.data.labels import EventLabel

@dataclass
class Node:
    id: str
    parents: list['IntermediateNode'] = field(default_factory=list, init=False)

@dataclass
class EventNode(Node):
    label: EventLabel = field(default=None)
    variable: str = field(default="it", init=False)
    condition: str = field(default="is present", init=False)

    def is_cause(self):
        return self.label.name[:-1] == 'Cause'

@dataclass
class IntermediateNode(Node):
    conjunction: bool = True
    children: list[Node] = field(default_factory=list, init=False)

    def add_children(self, children: list[Node]):
        self.children = self.children + children
        for child in children:
            child.parents.append(self)

    def remove_child(self, child: Node):
        if child in self.children:
            child.parents.remove(self)
            self.children.remove(child)

@dataclass
class Edge:
    start: Node = field(default=None)
    end: Node = field(default=None)
    negated: bool = False

@dataclass
class Graph:
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)