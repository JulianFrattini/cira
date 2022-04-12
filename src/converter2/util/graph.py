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

    def getRoot(self):
        if len(self.parents) == 0:
            return self
        return self.parents[0].getRoot()


class EventNode(Node):
    def __init__(self, cause: bool=True, variable: str = 'it', condition: str = 'is present'):
        super().__init__()
        self.cause = cause
        self.variable = variable
        self.condition = condition

    def __eq__(self, other):
        if not isinstance(other, EventNode):
            return False

        if self.cause == other.cause and self.variable == other.variable and self.condition == other.condition:
            return True
        return False

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

    def __eq__(self, other):
        if not isinstance(other, IntermediateNode):
            return False

        if self.conjunction != other.conjunction:
            return False

        if len(self.children) != len(other.children):
            return False

        for child in self.children:
            equalFound = False
            for otherchild in other.children:
                if child == otherchild:
                    equalFound = True
                    break

            if not equalFound:
                return False

        return True

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
    def __init__(self, rootcause: Node, effects: List[EventNode]):
        self.rootcause = rootcause
        self.effects = effects

    def generateTestCases(self):
        return None

    def __eq__(self, other):
        if self.rootcause != other.rootcause:
            return False

        for effect in self.effects:
            equalFound = False
            for othereffect in other.effects:
                if effect == othereffect:
                    equalFound = True
                    break

            if not equalFound:
                return False

        return True

    def __str__(self):
        effects = list(map(lambda e: str(e), self.effects))
        return str(self.rootcause) + ' => ' + ' && '.join(effects)