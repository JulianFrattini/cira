import json
from typing import Tuple

from src.converters.sentencetolabels.labelingconverter import connect_labels

from src.data.labels import Label, EventLabel, SubLabel
from src.data.graph import Node, IntermediateNode, EventNode, Edge, Graph

LABELS_EVENT = ['Cause1', 'Cause2', 'Cause3', 'Effect1', 'Effect2', 'Effect3']
LABELS_SUB = ['Conjunction', 'Disjunction', 'Variable', 'Condition', 'Negation']

def load_sentence(filename: str) -> Tuple[object, str, list[Label], Graph]:
    with open(filename, 'r') as f:
        file = json.load(f)

        sentence: str = file['text']
        labels: list[Label] = convert_labels(labels=file['labels'])
        graph: Graph = convert_graph(nodes=file['graph']['nodes'], edges=file['graph']['edges'])

        return (file, sentence, labels, graph)

def convert_labels(labels: list[dict]) -> list[Label]:
    """Generate a list of labels from the manually annotated labels of a static sentence file
    
    parameters:
        labels -- list of maually annotated labels
        
    returns: list of proper labels"""
    # extract all relevant labels
    result: list[Label] = []
    for label in labels:
        if label['label'] in LABELS_EVENT:
            result.append(EventLabel(id=label['id'], name=label['label'], begin=label['begin'], end=label['end']))
        elif label['label'] in LABELS_SUB:
            result.append(SubLabel(id=label['id'], name=label['label'], begin=label['begin'], end=label['end']))
    # recreate the connections between the labels
    connect_labels(labels=result)
    return result

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