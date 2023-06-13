import pytest

from src import model_locator
from src.api.service import CiRAServiceImpl

sentence: str = "If the button is pressed then the system shuts down."

labels: list[dict] = [
    {'id': 'L0', 'name': 'Cause1', 'begin': 3, 'end': 24, 'successor': {
        'id': 'L1', 'junctor': None}, 'children': ['L2', 'L4']},
    {'id': 'L1', 'name': 'Effect1', 'begin': 30, 'end': 51,
        'successor': None, 'children': ['L3', 'L5']},
    {'id': 'L2', 'name': 'Variable', 'begin': 3, 'end': 13, 'parent': 'L0'},
    {'id': 'L3', 'name': 'Variable', 'begin': 30, 'end': 40, 'parent': 'L1'},
    {'id': 'L4', 'name': 'Condition', 'begin': 14, 'end': 24, 'parent': 'L0'},
    {'id': 'L5', 'name': 'Condition', 'begin': 41, 'end': 51, 'parent': 'L1'},
]

graph = {
    'nodes': [{'id': 'E1', 'variable': 'the button', 'condition': 'is pressed'}, {'id': 'E0', 'variable': 'the system', 'condition': 'shuts down'}],
    'root': 'E1',
    'edges': [{'origin': 'E1', 'target': 'E0', 'negated': False}]
}

suite = {
    'conditions': [{'id': 'P0', 'variable': 'the button',
                    'condition': 'is pressed'}],
    'expected': [{'id': 'P1', 'variable': 'the system',
                  'condition': 'shuts down'}],
    'cases': [{'P0': True, 'P1': True}, {'P0': False, 'P1': False}]
}


@pytest.fixture(scope="module")
def sut() -> CiRAServiceImpl:
    # create the system under test
    service = CiRAServiceImpl(
        model_classification=model_locator.CLASSIFICATION, model_labeling=model_locator.LABELING)
    return service


@pytest.mark.integration
def test_classification(sut: CiRAServiceImpl):
    classification, confidence = sut.classify(sentence)
    assert classification == True
    assert confidence > 0.9


@pytest.mark.integration
def test_labeling(sut: CiRAServiceImpl):
    generated_labels = sut.sentence_to_labels(sentence)
    assert generated_labels == labels


@pytest.mark.integration
def test_graph(sut: CiRAServiceImpl):
    generated_graph = sut.sentence_to_graph(sentence, labels)
    assert generated_graph == graph


@pytest.mark.integration
def test_testsuite(sut: CiRAServiceImpl):
    generated_suite = sut.graph_to_test(graph, sentence)
    assert generated_suite == suite

