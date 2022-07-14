from src.data.graph import Graph, Node, EventNode
from src.data.test import Testsuite, Parameter

def convert(graph: Graph) -> Testsuite:

    # obtain all event nodes from the graph and generate a mapping from those nodes to parameters
    events = [node for node in graph.nodes if type(node) == EventNode]
    causes = [event for event in events if len(event.incoming) == 0]
    effects = [event for event in events if len(event.outgoing) == 0]
    input_parameters_map: dict = generate_parameters(nodes=causes)
    output_parameters_map: dict = generate_parameters(nodes=effects)

    expected_outcome: dict = get_expected_outcome(root_node_evaluation=True, effects=effects) + \
        get_expected_outcome(root_node_evaluation=False, effects=effects)

    return Testsuite(conditions=input_parameters_map.values(), expected=output_parameters_map.values(), cases=None)

def generate_parameters(nodes: list[EventNode]) -> dict:
    """Convert every node in the list into a parameter for a test suite
    
    parameters:
        nodes -- list of event nodes
        
    returns: a mapping between nodes and generated parameters"""

    return {node.id: Parameter(id=f'P{index}', variable=node.variable, condition=node.condition) for index, node in enumerate(nodes)}

def get_expected_outcome(root_node_evaluation: bool, effects: list[EventNode]) -> dict:
    """Generate a mapping of effect event nodes to an expected value.
    
    parameters:
        root_node_evaluation -- whether the root cause node is supposed to be evaluated to True or false
        effects -- list of event nodes that represent the effects in the cause-effect-graph
        
    returns: mapping from each effect to the expected value given the root node evaluation"""

    return {effect.id: (effect.incoming[0].negated != root_node_evaluation) for effect in effects}

def map_node_to_parameter(configuration: dict, parameters_map: dict) -> dict:
    """Convert a configuration, where a node is associated to a value, to a configuration, where a *parameter* is associated to a value.
    
    parameters:
        configuration -- mapping from nodes to values
        parameters_map -- mapping rom nodes to parameters
        
    returns: configuration which associates a parameter to a value"""
    
    return {parameters_map[config].id : configuration[config] for config in configuration}