import json
from typing import Tuple

from src.converters.sentencetolabels.labelingconverter import connect_labels

from src.data.labels import from_dict as labels_from_dict
from src.data.graph import from_dict as graph_from_dict
from src.data.test import from_dict as testsuite_from_dict

from src.data.labels import Label, EventLabel, SubLabel
from src.data.graph import Node, IntermediateNode, EventNode, Edge, Graph
from src.data.test import Suite, Parameter

LABELS_EVENT = ['Cause1', 'Cause2', 'Cause3', 'Effect1', 'Effect2', 'Effect3']
LABELS_SUB = ['Conjunction', 'Disjunction', 'Variable', 'Condition', 'Negation']

def load_sentence(filename: str) -> Tuple[object, str, list[Label], Graph, Suite]:
    """Load a sentence from a json file and convert the information into the internal representation of the pipeline. The json file is assumed to be in the format that is used for the static test files (currently to be found at the location specified in src.util.constants.SENTENCES_PATH).

    parameters:
        filename -- location of the json file

    returns:
        file -- pure file as read from the disc
        sentence -- the literal sentence
        labels -- list of labels as manually annotated on the sentence
        graph -- cause-effect graph representing the sentence
        testsuite -- test suite containing all parameters and all relevant test cases """
    with open(filename, 'r') as f:
        file = json.load(f)

        sentence: str = file['sentence']
        labels: list[Label] = labels_from_dict(serialized=file['labels'])#convert_labels(labels=file['labels'])
        graph: Graph = graph_from_dict(dict_graph=file['graph'])#convert_graph(nodes=file['graph']['nodes'], edges=file['graph']['edges'])
        testsuite: Suite = testsuite_from_dict(dict_suite=file['testsuite']) 
        """convert_testsuite(inputparams=file['testsuite']['inputparams'], 
            outputparams=file['testsuite']['outputparams'],
            cases=file['testsuite']['testcases'])"""

        return (file, sentence, labels, graph, testsuite)

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

def convert_testsuite(inputparams: list[dict], outputparams: list[dict], cases: list[dict]) -> Suite:
    """Generate a test suite in the internal representation from the given parameters and cases.
    
    parameters:
        inputparams -- list of parameters, specifying both an id and a variable (as 'text')
        outputparams -- list of parameters, specifying both an id and a variable (as 'text')
        cases -- list of test cases, specifying the 'configuration' (input) and the outcome

    returns: a test suite representing all involved parameters and relevant configurations"""
    # generate all parameters (both for the input (i.e., "configurations") and the output (i.e., "expected outcomes"))
    parameters = {}
    for inp in [True, False]:
        parameters['input' if inp else 'output'] = [Parameter(id=f'P{param["id"]}', variable=param['text'], condition=get_parameter_condition(param["id"], cases, inp)) for param in (inputparams if inp else outputparams)]

    # generate a list of all test cases
    test_cases: list[dict] = []
    for case in cases:
        tc_conditions = {f'P{param["inputid"]}': not param['text'].startswith('not') for param in case['configurations']}
        tc_expected = {f'P{param["outputid"]}': not param['text'].startswith('not') for param in case['outcome']}
        test_cases.append(tc_conditions | tc_expected)

    # assemble and return the test suite
    return Suite(conditions=parameters['input'], expected=parameters['output'], cases=test_cases)

def get_parameter_condition(id: int, cases: list[dict], input: bool) -> str:
    """Extract the condition value of a parameter from a test case configuration. Because the static json data has the information about the condition text located in the test cases instead of in the parameters themselves, they need to be extracted.
    
    parameters:
        id -- identifier of the parameter in question
        cases -- list of test cases in which the parameter appears and has its condition defined
        input -- true, if the parameter is an input parameter
        
    returns: literal condition of the parameter """
    # determine the correct keys
    parameter_list = "configurations" if input else "outcome"
    id_key = f'{"input" if input else "output"}id'

    # identify the parameter in the list of test cases
    parameter_configuration = [parameter for parameter in cases[0][parameter_list] if parameter[id_key] == id]

    # format the literal condition by removing the potential prefix 'not'
    condition = parameter_configuration[0]["text"]
    if condition.startswith('not '):
        condition = condition[4:]

    return condition