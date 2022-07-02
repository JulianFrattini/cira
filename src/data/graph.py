from ast import List
from dataclasses import dataclass, field

from src.data.labels import EventLabel

@dataclass
class Node:
    id: str
    parents: list['Edge'] = field(default_factory=list, init=False)

@dataclass
class EventNode(Node):
    label: EventLabel = field(default=None)
    variable: str = field(default="it", init=False)
    condition: str = field(default="is present", init=False)

    def is_cause(self):
        return self.label.name[:-1] == 'Cause'

    def is_negated(self):
        return len([label for label in self.label.children if label.name == 'Negation']) > 0

    def __repr__(self):
        return f'[{self.variable}].({self.condition})'

@dataclass
class IntermediateNode(Node):
    conjunction: bool = True
    children: list['Edge'] = field(default_factory=list, init=False)

    def add_child(self, child: Node, negated: bool=False):
        edge = Edge(self, child, negated=negated)
        self.children.append(edge)
        child.parents.append(edge)

    def remove_child(self, child: 'Node'):
        for edge in [edge for edge in self.children if edge.target==child]:
            self.children.remove(edge)

    def __repr__(self):
        cstring = [('NOT ' if child.negated else '') + str(child.target) for child in self.children]
        jstring = ' && ' if self.conjunction else ' || '
        return f'({jstring.join(cstring)})'

@dataclass
class Edge:
    origin: Node = field(default=None)
    target: Node = field(default=None)
    negated: bool = False

    def __repr__(self):
        return f'{str(self.origin.id)} -{"~" if self.negated else "-"}-> {str(self.target.id)}'

@dataclass
class Graph:
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)