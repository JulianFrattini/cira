from src.data.graph import Graph, Node, EventNode
from src.data.test import Testsuite, Parameter

def convert(graph: Graph) -> Testsuite:

    # obtain all event nodes from the graph and generate a mapping from those nodes to parameters
    events = [node for node in graph.nodes if type(node) == EventNode]
    parameters = generate_parameters(nodes=events)
    causes = [event for event in events if len(event.incoming) == 0]
    effects = [event for event in events if len(event.outgoing) == 0]

    for root_node_evaluation in [True, False]:
        outcome: dict = get_expected_outcome(root_node_evaluation=root_node_evaluation, effects=effects)

    return Testsuite(conditions=None, expected=None, cases=None)

def generate_parameters(nodes: list[EventNode]) -> dict:
    """Convert every node in the list into a parameter for a test suite
    
    parameters:
        nodes -- list of event nodes
        
    returns: a mapping between nodes and generated parameters"""

    return {node: Parameter(id=f'P{index}', variable=node.variable, condition=node.condition) for index, node in enumerate(nodes)}

def get_expected_outcome(root_node_evaluation: bool, effects: list[EventNode]) -> dict:
    """Generate a mapping of effect event nodes to an expected value.
    
    parameters:
        root_node_evaluation -- whether the root cause node is supposed to be evaluated to True or false
        effects -- list of event nodes that represent the effects in the cause-effect-graph
        
    returns: mapping from each effect to the expected value given the root node evaluation"""

    return {effect: (effect.incoming[0].negated == root_node_evaluation) for effect in effects}