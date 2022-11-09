import json
from typing import Tuple

from src.data.labels import from_dict as labels_from_dict
from src.data.graph import from_dict as graph_from_dict
from src.data.test import from_dict as testsuite_from_dict

from src.data.labels import Label
from src.data.graph import Graph
from src.data.test import Suite

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
        labels: list[Label] = labels_from_dict(serialized=file['labels'])
        graph: Graph = graph_from_dict(dict_graph=file['graph'])
        testsuite: Suite = testsuite_from_dict(dict_suite=file['testsuite'])

        return (file, sentence, labels, graph, testsuite)