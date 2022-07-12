import pytest, json

from src.data.graph import Node, IntermediateNode, EventNode, Edge, Graph

SENTENCES_PATH = './test/static/sentences/'
LABELS_EVENT = ['Cause1', 'Cause2', 'Cause3', 'Effect1', 'Effect2', 'Effect3']
LABELS_SUB = ['Conjunction', 'Disjunction', 'Variable', 'Condition', 'Negation']


@pytest.fixture
def sentence(id: str):
    with open(f'{SENTENCES_PATH}sentence{id}.json', 'r') as f:
        file = json.load(f)
        graph = convert_graph(nodes=file['graph']['nodes'], edges=file['graph']['edges'])

        return {
            'text': file['text'],
            'graph': graph
        }

def convert_graph(nodes: list[dict], edges: list[dict]) -> Graph:
    """Generate a graph in the internal representation from the given nodes and edges in the document.
    
    parameters:
        nodes -- list of event and intermediate nodes
        edges -- list of edges between the nodes
        
    returns: a graph representing the nodes and edges"""

    # generate the nodes
    nodelist: list[Node] = []
    for node in nodes:
        if 'type' not in node:
            event = EventNode(id=f'N{node["id"]}', label=None)
            event.variable = node['variable']
            event.condition = node['condition']
            nodelist.append(event)
        else:
            nodelist.append(IntermediateNode(id=f'N{node["id"]}', conjunction=(node["type"]=='AND')))
    
    # generate the edges
    edgelist: list[Edge] = []
    for edge in edges:
        source: Node = [node for node in nodelist if node.id == f'N{edge["source"]}'][0]
        target: Node = [node for node in nodelist if node.id == f'N{edge["target"]}'][0]

        edge = target.add_incoming(child=source, negated=edge["negate"])
        edgelist.append(edge)
        
    # determine the root
    effectnodes = [node for node in nodelist if len(node.outgoing) == 0]
    root = effectnodes[0].incoming[0].origin

    return Graph(nodes=nodelist, root=root, edges=edgelist)

# test for sentences 6 and 6b
@pytest.mark.parametrize('id', ['6'])
def test_test(sentence):
    print(sentence)

    graph: Graph = sentence['graph']
    configurations = []
    for expected in [True, False]:
        configurations = configurations + graph.root.get_testcase_configuration(expected_outcome=expected)
    print(configurations)

    assert True

"""def equals(manual_configurations: list, generated_configurations: list) -> bool:
    if len(manual_configurations) != len(generated_configurations):
        return False

    for mconf in manual_configurations:
        equivalent = [candidate for candidate in generated_configurations if ]"""