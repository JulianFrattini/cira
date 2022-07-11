from abc import abstractmethod
from dataclasses import dataclass, field

from src.data.labels import EventLabel

@dataclass
class Node:
    id: str
    outgoing: list['Edge'] = field(default_factory=list, init=False)
    incoming: list['Edge'] = field(default_factory=list, init=False)

    def add_incoming(self, child: 'Node', negated: bool=False) -> 'Edge':
        edge = Edge(origin=child, target=self, negated=negated)
        self.incoming.append(edge)
        child.outgoing.append(edge)
        return edge

    def remove_incoming(self, child: 'Node'):
        for edge in [edge for edge in self.incoming if edge.origin==child]:
            edge.origin.outgoing.remove(edge)
            self.incoming.remove(edge)

    def rewire(self, old_child: 'Node', new_child: 'Node'):
        self.remove_incoming(old_child)
        self.add_incoming(new_child)

    def get_root(self):
        """Assuming that the graph is currently structured like a tree (which the subgraph only containing causes is), return the root node.
        
        returns: root node with no outgoing edges"""
        if len(self.outgoing) == 0:
            return self
        return self.outgoing[0].target.get_root()

    @abstractmethod
    def get_testcase_configuration(self, expected_outcome: bool, negated: bool) -> list[dict]:
        pass

    @abstractmethod
    def is_equal(self, other, incoming: bool) -> bool:
        pass

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

    def condense(self) -> list['Edge']:
        """In case the event node has more than one outgoing relationship, try to condense these relationships. If they have the same junctor type, merge them. If not, rearrange them according to precedence rules (AND binds stronger than OR)
        
        returns: list of edges that are now removable"""
        removable_edges: list[Edge] = []
        if len(self.outgoing) > 0:
            conjunction_parents = [out for out in self.outgoing if out.target.conjunction]
            if len(conjunction_parents) == len(self.outgoing) or len(conjunction_parents) == 0:
                # simple case: all parents have the same junctor type
                surviving_parent: IntermediateNode = self.outgoing[0].target
                for parent in self.outgoing[1:]:
                    removable = surviving_parent.merge(parent.target)
                    removable_edges = removable_edges + removable
            else: 
                # complex case: apply precedence rules
                disjunction_edge = [parent for parent in self.outgoing if not parent.target.conjunction][0]
                disjunction_parent: IntermediateNode = disjunction_edge.target
                disjunction_parent.rewire(old_child=self, new_child=conjunction_parents[0].target)
        return removable_edges

    def flatten(self) -> list['Node']:
        return [self]

    def get_testcase_configuration(self, expected_outcome: bool, negated: bool) -> list[dict]:
        return {self.id : (expected_outcome != negated)}

    def is_equal(self, other, incoming: bool) -> bool:
        if type(other) != EventNode:
            return False
        return self.variable == other.variable and self.condition == other.condition

    def __repr__(self):
        return f'[{self.variable}].({self.condition})'

@dataclass
class IntermediateNode(Node):
    conjunction: bool = True

    def merge(self, other: 'IntermediateNode') -> list['Edge']:
        """Merge this intermediate node with another intermediate node. In the end, all nodes with an incoming connection to the other node, which are not yet connected to this node, will be connected to this node.
        
        parameters:
            other -- the other node to merge with
            
        returns: list of unused egdes which now can be removed"""
        current_inputs = [inc.origin for inc in self.incoming]
        removable_edges: list[Edge] = []
        for potential_input in other.incoming:
            if potential_input.origin not in current_inputs:
                potential_input.target = self
                self.incoming.append(potential_input)
            else:
                potential_input.origin.outgoing.remove(potential_input)
                removable_edges.append(potential_input)
        return removable_edges


    def flatten(self) -> list['Node']:
        result = [self]
        for child in self.incoming:
            result = result + child.origin.flatten()
        return result

    def get_testcase_configuration(self, expected_outcome: bool, negated: bool) -> list[dict]:
        # for a conjunction to be evaluated to true or a disjunction to be evaluated to false only one configuration is possible
        inc_configs = []
        if (expected_outcome and self.conjunction) or (not expected_outcome and not self.conjunction):
            # for every incoming node, get the configurations for the expected outcome
            inc_configs.append([inc.origin.get_testcase_configuration(expected_outcome, (negated and inc.negated)) for inc in self.incoming])
        else:
            for oddone in self.incoming:
                inc_configs.append([inc.origin.get_testcase_configuration(expected_outcome, not (negated and inc.negated) if (inc != oddone) else (negated and inc.negated)) for inc in self.incoming])
        
        """configurations = []
        for inc_config in inc_configs:
            configuration = []
            for inc in inc_config:
                configs = inc_config[inc]
                if len(configuration) == 0:
                    configuration.append(configs)
                else: 
                    to_multiply = configuration.copy()
                    configuration = []
                    for config1 in to_multiply:
                        for config2 in configs:
                            configuration.append(config1 + configs[config2])
            configurations = configurations + configuration"""

        return inc_configs

    def is_equal(self, other, incoming: bool) -> bool:
        if type(other) != IntermediateNode or self.conjunction != other.conjunction:
            return False

        to_check = "incoming" if incoming else "outgoing"

        if len(getattr(self, to_check)) != len(getattr(other, to_check)):
            return False

        for inc in getattr(self, to_check):
            equivalent = [eq for eq in getattr(other, to_check) if (inc.negated == eq.negated and inc.origin.is_equal(other=eq.origin, incoming=incoming))]
            if len(equivalent) != 1:
                return False

        return True

    def __repr__(self):
        inp = [('NOT ' if input.negated else '') + str(input.origin) for input in self.incoming]
        jstring = ' && ' if self.conjunction else ' || '

        result = f'({jstring.join(inp)})'
        return result

@dataclass
class Edge:
    origin: Node = field(default=None)
    target: Node = field(default=None)
    negated: bool = False

    def __repr__(self):
        return f'{str(self.origin.id)} -{"~" if self.negated else "-"}-> {str(self.target.id)}'

    def __eq__(self, other: 'Edge') -> bool:
        return self.negated == other.negated and self.origin == other.origin and self.target == other.target

@dataclass
class Graph:
    nodes: list[Node] = field(default_factory=list)
    root: Node = None,
    edges: list[Edge] = field(default_factory=list)

    def __repr__(self):
        effects = " && ".join([('NOT ' if out.negated else '') + str(out.target) for out in self.root.outgoing])
        return f'{str(self.root)} ===> {effects}'

    def __eq__(self, other: 'Graph') -> bool:
        # check that the effects are equal
        if len(self.root.outgoing) != len(other.root.outgoing):
            return False
        for effect_edge in self.root.outgoing:
            equivalent = [eq_edge for eq_edge in other.root.outgoing if (eq_edge.negated == effect_edge.negated and effect_edge.target.is_equal(other=eq_edge.target, incoming=False))]
            if len(equivalent) != 1:
                return False

        # check that the causes are equal
        return self.root.is_equal(other=other.root, incoming=True)