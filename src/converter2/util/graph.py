from abc import abstractmethod


class Node:
    @abstractmethod
    def __str__(self):
        pass

class Event(Node):
    def __init__(self, variable: str = 'it', condition: str = 'is present'):
        self.variable = variable
        self.condition = condition

class Intermediate(Node):
    def __init__(self, conjunction: bool=True):
        self.conjunction = conjunction

class Edge:
    def __init__(self, source: Node, target: Node, negated: bool=False):
        self.source = source
        self.target = target
        self.negated = negated