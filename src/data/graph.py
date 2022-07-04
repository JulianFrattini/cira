from abc import abstractmethod
from dataclasses import dataclass, field

from src.data.labels import EventLabel

@dataclass
class Node:
    id: str
    parents: list['Edge'] = field(default_factory=list, init=False)

    def get_root(self):
        if len(self.parents) == 0:
            return self
        return self.parents[0].origin.get_root()

    @abstractmethod
    def flatten(self) -> list['Node']:
        pass

@dataclass
class EventNode(Node):
    label: EventLabel = field(default=None)
    variable: str = field(default="it", init=False)
    condition: str = field(default="is present", init=False)

    def is_cause(self):
        return self.label.is_cause()

    def is_negated(self):
        return len([label for label in self.label.children if label.name == 'Negation']) > 0

    def condense(self):
        """In case the event node has more than one parent, try to condense these parents. If they have the same junctor type, merge them. If not, rearrange them according to precedence rules (AND binds stronger than OR)"""
        if len(self.parents) > 0:
            conjunction_parents = [parent for parent in self.parents if parent.origin.conjunction]
            if len(conjunction_parents) == len(self.parents) or len(conjunction_parents) == 0:
                # simple case: all parents have the same junctor type
                surviving_parent: IntermediateNode = self.parents[0].origin
                for parent in self.parents[1:]:
                    surviving_parent.merge(parent.origin)
            else: 
                # complex case: apply precedence rules
                disjunction_edge = [parent for parent in self.parents if not parent.origin.conjunction][0]
                disjunction_parent: IntermediateNode = disjunction_edge.origin
                disjunction_parent.rewire(old_child=self, new_child=conjunction_parents[0].origin)

    def flatten(self) -> list['Node']:
        return [self]

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
            edge.target.parents.remove(edge)
            self.children.remove(edge)

    def merge(self, other: 'IntermediateNode'):
        """Merge this node with another intermediate node"""
        child_targets = [child.target for child in self.children]
        for child in other.children:
            if child.target not in child_targets:
                child.origin = self
                self.children.append(child)
            else:
                child.target.parents.remove(child)

    def rewire(self, old_child: Node, new_child: Node):
        self.remove_child(old_child)
        self.add_child(new_child)

    def flatten(self) -> list['Node']:
        result = [self]
        for child in self.children:
            result = result + child.target.flatten()
        return result

    def __repr__(self):
        cstring = [('NOT ' if child.negated else '') + str(child.target) for child in self.children]
        jstring = ' && ' if self.conjunction else ' || '

        result = f'({jstring.join(cstring)})'
        return result

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
    root: Node = None,
    edges: list[Edge] = field(default_factory=list)

    def __repr__(self):
        effects = " && ".join([('NOT ' if parent.negated else '') + str(parent.target) for parent in self.root.parents])
        return f'{str(self.root)} ===> {effects}'