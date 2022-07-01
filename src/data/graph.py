from ast import List
from dataclasses import dataclass, field

from src.data.labels import EventLabel

@dataclass
class Node:
    id: str

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

@dataclass
class Edge:
    start: Node = field(default=None)
    end: Node = field(default=None)
    negated: bool = False

@dataclass
class Graph:
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)