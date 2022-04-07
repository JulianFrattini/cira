from abc import abstractmethod
from typing import List

class Node:
    def __init__(self):
        self.parents = []

    def getParents(self):
        return self.parents

    def addParent(self, parent: 'Node'):
        self.parents.append(parent)

    def removeParent(self, parent: 'Node'):
        self.parents.remove(parent)

    @abstractmethod
    def __str__(self):
        pass

class EventNode(Node):
    def __init__(self, variable: str = 'it', condition: str = 'is present'):
        super().__init__()
        self.variable = variable
        self.condition = condition

    def __str__(self):
        return f'[{self.variable}].({self.condition})'

class IntermediateNode(Node):
    def __init__(self, conjunction: bool=True, children=List[Node]):
        super().__init__()
        self.conjunction = conjunction
        self.children = children
        for child in self.children:
            child.addParent(self)

    def getChildren(self):
        return self.children
    
    def addChild(self, child: Node):
        self.children.append(child)

    def removeChild(self, child: Node):
        self.children.remove(child)

    def isConjunction(self):
        return self.conjunction

    def rewire(self, origin: Node, target: Node):
        # remove the old child
        origin.removeParent(self)
        self.children.remove(origin)

        target.addParent(self)
        self.children.append(target)

    def __str__(self):
        childstrings = []
        for child in self.children:
            if isinstance(child, IntermediateNode):
                childstrings.append(f'({str(child)})')
            else:
                childstrings.append(str(child))

        symbol = ' && ' if self.conjunction else ' || '
        result = symbol.join(childstrings)
        return result

class Edge:
    def __init__(self, source: Node, target: Node, negated: bool=False):
        self.source = source
        self.target = target
        self.negated = negated


class Graph:
    def __init__(self, nodes: List[Node]):
        self.nodes = nodes

    def generateTestCases(self):
        return None