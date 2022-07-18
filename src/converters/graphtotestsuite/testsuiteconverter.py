from src.data.graph import Graph, EventNode
from src.data.test import Suite, Parameter#, Configuration

def convert(graph: Graph) -> Suite:
    """Generate a test suite from a cause-effect graph. The test suite contains one parameter per event node (cause-nodes become input-/condition-parameters, effect-nodes become (expected) outcome parameters) and a minimal list of test cases necessary to evaluate the root cause node both to true and false, effectively covering all relevant, unique configurations of parameters which would assert that a system exhibits the behavior entailed by the cause-effect graph.

    parameters: 
        graph -- a cause-effect graph representing a causal sentence

    returns: a minimal test suite that describes how to assert that a system exhibits the behavior entailed by the graph."""
    # obtain all event nodes from the graph and generate a mapping from those nodes to parameters
    events = [node for node in graph.nodes if type(node) == EventNode]
    causeids = [event.id for event in events if len(event.incoming) == 0]
    effects = [event for event in events if len(event.outgoing) == 0]
    effectids = [event.id for event in events if len(event.outgoing) == 0]

    # generate all parameters from the events
    parameters_map: dict = generate_parameters(nodes=events)
    input_parameters_map: dict = {node: parameters_map[node] for node in parameters_map if node in causeids}
    output_parameters_map: dict = {node: parameters_map[node] for node in parameters_map if node in effectids}

    # generate the test cases
    test_cases = []
    for root_node_outcome in [True, False]:
        outcome_configuration: dict = get_expected_outcome(root_node_evaluation=root_node_outcome, effects=effects)
        expected_outcome = map_node_to_parameter(configuration=outcome_configuration, parameters_map=parameters_map)

        node_configurations: list[dict] = graph.root.get_testcase_configuration(expected_outcome=root_node_outcome)
        for config in node_configurations:
            test_case = map_node_to_parameter(configuration=config, parameters_map = parameters_map)
            
            #test_cases.append(Configuration(conditions=test_case, expected=expected_outcome))
            test_cases.append(test_case | expected_outcome)

    return Suite(conditions=list(input_parameters_map.values()), expected=list(output_parameters_map.values()), cases=test_cases)

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