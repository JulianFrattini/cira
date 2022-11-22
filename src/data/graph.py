from abc import abstractmethod
from dataclasses import dataclass, field
import itertools

from src.data.labels import EventLabel, SubLabel


@dataclass
class Node:
    id: str
    outgoing: list['Edge'] = field(default_factory=list, init=False)
    incoming: list['Edge'] = field(default_factory=list, init=False)

    def add_incoming(self, child: 'Node', negated: bool = False) -> 'Edge':
        edge = Edge(origin=child, target=self, negated=negated)
        self.incoming.append(edge)
        child.outgoing.append(edge)
        return edge

    def remove_incoming(self, child: 'Node') -> list['Edge']:
        removed = []
        for edge in [edge for edge in self.incoming if edge.origin == child]:
            edge.origin.outgoing.remove(edge)
            self.incoming.remove(edge)
            removed.append(edge)
        return removed

    def rewire(self, old_child: 'Node', new_child: 'Node') -> tuple[list['Edge'], 'Edge']:
        old_edges = self.remove_incoming(old_child)
        new_edge = self.add_incoming(new_child)
        return (old_edges, new_edge)

    def get_root(self):
        """Assuming that the graph is currently structured like a tree (which the subgraph only containing causes is), return the root node.

        returns: root node with no outgoing edges"""
        if len(self.outgoing) == 0:
            return self
        return self.outgoing[0].target.get_root()

    @abstractmethod
    def get_testcase_configuration(self, expected_outcome: bool) -> list[dict]:
        pass

    @abstractmethod
    def is_equal(self, other, incoming: bool) -> bool:
        pass

    @abstractmethod
    def flatten(self) -> list['Node']:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        pass


@dataclass
class EventNode(Node):
    labels: list[EventLabel] = field(default_factory=list)
    variable: str = field(default="it")
    condition: str = field(default="is present")

    def is_cause(self):
        """Determine whether this node represents a cause.

        returns: True, if the event label of this node is a cause label"""
        return self.labels[0].is_cause()

    def is_negated(self):
        """Determine whether this event node is negated.

        returns: True, if the event label of this node has a child label of type Negation"""
        all_sublabels: list[SubLabel] = []
        for label in self.labels:
            all_sublabels = all_sublabels + label.children

        return len([label for label in all_sublabels if label.name == 'Negation']) > 0

    def condense(self) -> tuple[list['Edge'], list['Edge']]:
        """In case the event node has more than one outgoing relationship, try to condense these relationships. If they have the same junctor type, merge them. If not, rearrange them according to precedence rules (AND binds stronger than OR)

        returns: a tuple containing 
          a list of edges that are now removable,
          a list of edges that are now new"""
        removable_edges: list[Edge] = []
        new_edges: list[Edge] = []
        if len(self.outgoing) > 0:
            conjunction_parents = [
                out for out in self.outgoing if out.target.conjunction]
            if len(conjunction_parents) == len(self.outgoing) or len(conjunction_parents) == 0:
                # simple case: all parents have the same junctor type
                surviving_parent: IntermediateNode = self.outgoing[0].target
                for parent in self.outgoing[1:]:
                    removable = surviving_parent.merge(parent.target)
                    removable_edges = removable_edges + removable
            else:
                # complex case: apply precedence rules
                disjunction_edge = [
                    parent for parent in self.outgoing if not parent.target.conjunction][0]
                disjunction_parent: IntermediateNode = disjunction_edge.target
                edges_to_remove, edge_to_add = disjunction_parent.rewire(
                    old_child=self, new_child=conjunction_parents[0].target)
                removable_edges = removable_edges + edges_to_remove
                new_edges.append(edge_to_add)
        return (removable_edges, new_edges)

    def flatten(self) -> list['Node']:
        return [self]

    def get_testcase_configuration(self, expected_outcome: bool) -> list[dict]:
        return [{self.id: expected_outcome}]

    def is_equal(self, other, incoming: bool) -> bool:
        if type(other) != EventNode:
            return False
        return self.variable == other.variable and self.condition == other.condition

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'variable': self.variable,
            'condition': self.condition
        }

    def __repr__(self):
        return f'[{self.variable}].({self.condition})'


@dataclass
class IntermediateNode(Node):
    conjunction: bool = True
    precedence: bool = False # if conjunction is false but precedence true then this intermediate node has to be resolved before the others

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
        """Translate the tree structure implied by this intermediate node into a flat list.

        returns: list containing all (leaf and intermediate) nodes """
        result = [self]
        for child in self.incoming:
            result = result + child.origin.flatten()
        return result

    def get_testcase_configuration(self, expected_outcome: bool) -> list[dict]:
        """Generate a map of configurations which determines the value that each leaf node connected to this intermediate node needs to have in order to produce the expected outcome.

        parameters:
            expected_outcome -- the boolean value this intermediate node is expected to have

        returns: list of configurations mapping leaf (Event) node ids to boolean values
        """
        if (expected_outcome == self.conjunction):
            # for a conjunction to be evaluated to true or a disjunction to false only one configuration is possible: every incoming node has to have the same expected outcome (negated if necessary)
            inc_configs = [inc.origin.get_testcase_configuration(
                expected_outcome != inc.negated) for inc in self.incoming]
            return permute_configurations(inc_configs=inc_configs)
        else:
            # for a conjunction to be evaluated to false or disjunction to true, generate one configuration per incoming edge, where all other incoming nodes are evaluated to the opposite value (conjunction: true, disjunction: false) and only the respective incoming node is evaluated to the expected value (conjunction: false, disjunction: true) (adjust for negations)
            configurations = []
            for oddone in self.incoming:
                inc = [inc.origin.get_testcase_configuration((expected_outcome == inc.negated) if (
                    inc != oddone) else (expected_outcome != inc.negated)) for inc in self.incoming]
                configurations = configurations + \
                    permute_configurations(inc_configs=inc)
            return configurations

    def is_equal(self, other, incoming: bool) -> bool:
        """Determine whether this node is equal to another node.

        parameters:
            other -- the other object with which this one is compared
            incoming -- True, if the direction of the recursive check is upstream

        returns: True, if this object is equal to the given other object"""
        # assert that both the type and the conjunction of the other node is the same
        if type(other) != IntermediateNode or self.conjunction != other.conjunction:
            return False

        # depending on the direction to check, select the list of edges to continue on
        to_check = "incoming" if incoming else "outgoing"
        if len(getattr(self, to_check)) != len(getattr(other, to_check)):
            return False

        for inc in getattr(self, to_check):
            equivalent = [eq for eq in getattr(other, to_check) if (
                inc.negated == eq.negated and inc.origin.is_equal(other=eq.origin, incoming=incoming))]
            # if there is not exactly one equivalent for each edge in the the selected list of edges, the objects are inequal
            if len(equivalent) != 1:
                return False

        return True

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'conjunction': self.conjunction
        }

    def __repr__(self):
        inp = [('NOT ' if input.negated else '') + str(input.origin)
               for input in self.incoming]
        jstring = ' && ' if self.conjunction else ' || '

        result = f'({jstring.join(inp)})'
        return result


def permute_configurations(inc_configs: list) -> list[dict]:
    """Permute an automatically generated list of individual configurations for incoming nodes of an intermediate node. Every incoming node has 1..n individual configurations (at max 2^n, where n is the number of connected leaf nodes) which are permuted with all other individual configurations

    parameters:
        inc_configs -- individual configurations of the incoming nodes

    returns: harmonized, permuted set of configurations of all incoming nodes"""

    configurations = []
    for inc_config in inc_configs:
        if len(configurations) == 0:
            # if this is the first individual configuration to consider, simply add it to the list of configurations
            configurations = inc_config
        else:
            # otherwise, generate the product between the existing configurations and the individual configurations of this node (inc_config)
            configurations = [(r[0] | r[1])
                              for r in itertools.product(configurations, inc_config)]

    return configurations


@dataclass
class Edge:
    origin: Node = field(default=None)
    target: Node = field(default=None)
    negated: bool = False

    def to_dict(self) -> dict:
        return {'origin': self.origin.id, 'target': self.target.id, 'negated': self.negated}

    def __repr__(self):
        return f'{str(self.origin.id)} -{"~" if self.negated else "-"}-> {str(self.target.id)}'

    def __eq__(self, other: 'Edge') -> bool:
        return self.negated == other.negated and self.origin == other.origin and self.target == other.target


@dataclass
class Graph:
    nodes: list[Node] = field(default_factory=list)
    root: Node = None,
    edges: list[Edge] = field(default_factory=list)

    def get_node(self, id: str):
        """Find and return the node of this graph with the given id.

        parameters:
            id -- identifier used by the node in question

        returns: the node within this graph with the given id, None if it does not exist"""
        candidates = [node for node in self.nodes if node.id == id]
        if len(candidates) == 0:
            print(f'No node with id {id} found in {self.nodes}')
            return None
        return candidates[0]

    def to_dict(self) -> dict:
        """Convert a graph into a dictionary object, effectively also replacing all cyclic dependencies (caused by edges) by references.

        returns: graph as a dictionary"""

        edges_serialized: list[dict] = [edge.to_dict() for edge in self.edges]
        nodes_serialized: list[dict] = [node.to_dict() for node in self.nodes]

        return {
            'nodes': nodes_serialized,
            'root': self.root.id,
            'edges': edges_serialized
        }

    def __repr__(self):
        effects = " && ".join(
            [('NOT ' if out.negated else '') + str(out.target) for out in self.root.outgoing])
        return f'{str(self.root)} ===> {effects}'

    def __eq__(self, other: 'Graph') -> bool:
        # check that the effects are equal
        if len(self.root.outgoing) != len(other.root.outgoing):
            return False
        for effect_edge in self.root.outgoing:
            equivalent = [eq_edge for eq_edge in other.root.outgoing if (
                eq_edge.negated == effect_edge.negated and effect_edge.target.is_equal(other=eq_edge.target, incoming=False))]
            if len(equivalent) != 1:
                return False

        # check that the causes are equal
        return self.root.is_equal(other=other.root, incoming=True)


def from_dict(dict_graph: dict) -> Graph:
    """Convert a graph represented by a dictionary into an actual graph object. This recovers references between edges and nodes from the ids.

    parameters:
        dict_graph -- graph as a dictionary

    returns: actual graph representing the dict_graph"""

    # recover the nodes
    nodes: list[Node] = []
    for node in dict_graph['nodes']:
        if 'conjunction' in node.keys():
            nodes.append(IntermediateNode(
                id=node['id'], conjunction=node['conjunction']))
        else:
            nodes.append(EventNode(
                id=node['id'], variable=node['variable'], condition=node['condition']))

    # recover the edges
    edges = []
    for edge in dict_graph['edges']:
        origin = get_node_from_list(nodes, edge['origin'])
        target = get_node_from_list(nodes, edge['target'])
        edges.append(target.add_incoming(origin, negated=edge['negated']))

    # recover the root
    root = get_node_from_list(nodes, dict_graph['root'])

    return Graph(nodes=nodes, root=root, edges=edges)


def get_node_from_list(nodelist: list[Node], id: str):
    """Obtain a node from a list of nodes by its id

    parameters:
        nodelist -- list of nodes
        id -- identifier of the requested node

    returns:
        node -- Node with the requested id if it exists,
        None -- otherwise"""
    candidates = [node for node in nodelist if node.id == id]
    if len(candidates) == 0:
        return None
    if len(candidates) > 1:
        print(
            f'Warning: searching for node {id} in {nodelist} yielded mulitple results')
    return candidates[0]
