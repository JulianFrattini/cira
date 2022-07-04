import pytest, json

from src.converters.labelstograph.graphconverter import GraphConverter
from src.converters.labelstograph.eventresolver import SimpleResolver

from src.converters.sentencetolabels.labelingconverter import connect_labels

from src.data.labels import Label, EventLabel, SubLabel
from src.data.graph import Graph, Node, IntermediateNode, EventNode, Edge

SENTENCES_PATH = './test/static/sentences/'
LABELS_EVENT = ['Cause1', 'Cause2', 'Cause3', 'Effect1', 'Effect2', 'Effect3']
LABELS_SUB = ['Conjunction', 'Disjunction', 'Variable', 'Condition', 'Negation']

@pytest.fixture
def sut() -> GraphConverter:
    return GraphConverter(eventresolver=SimpleResolver())

@pytest.fixture
def sentence(id: str):
    with open(f'{SENTENCES_PATH}sentence{id}.json', 'r') as f:
        file = json.load(f)

        # extract all relevant labels
        labels: list[Label] = []
        for label in file['labels']:
            if label['label'] in LABELS_EVENT:
                labels.append(EventLabel(id=label['id'], name=label['label'], begin=label['begin'], end=label['end']))
            elif label['label'] in LABELS_SUB:
                labels.append(SubLabel(id=label['id'], name=label['label'], begin=label['begin'], end=label['end']))
        connect_labels(labels)
        graph = convert_graph(nodes=file['graph']['nodes'], edges=file['graph']['edges'])

        return {
            'text': file['text'],
            'labels': labels,
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

# currently excluded: sentence 16 (split cause1), 10 & 11 (for exceptive clauses), 17 (overruled precedence)
@pytest.mark.parametrize('id', ['1', '1b', '1c', '2', '3', '4', '5', '6', '6b', '7', '8', '12', '13', '14'])
def test_graphconverter(sentence, sut: GraphConverter):
    graph = sut.generate_graph(sentence['text'], sentence['labels'])
    assert sentence['graph'] == graph
