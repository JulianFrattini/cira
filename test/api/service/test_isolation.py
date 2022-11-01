import pytest
import unittest.mock as mock
from unittest.mock import patch

from src.api.service import CiRAServiceImpl

from src.data.labels import SubLabel
from src.data.graph import Graph, EventNode
from src.data.test import Suite, Parameter

# since the CiRAConverter is mocked in this test suite, define all objects (and their appropriate serialization) in advance
sentence = "If the button is pressed then the system shuts down."

classification = (True, 0.84)

labels = [SubLabel(id='L1', name='Variable', begin=10, end=15)]
labels_serialized = [{'id': 'L1', 'name': 'Variable',
                      'begin': 10, 'end': 15, 'parent': None}]

nodes = [EventNode(id='c', variable='the button', condition='is pressed'), EventNode(
    id='e', variable='the system', condition='shuts down')]
edge = nodes[1].add_incoming(nodes[0])
graph = Graph(nodes=nodes, root=nodes[0], edges=[edge])
graph_serialized = {
    'nodes': [{'id': 'c', 'variable': 'the button', 'condition': 'is pressed'}, {'id': 'e', 'variable': 'the system', 'condition': 'shuts down'}],
    'root': 'c',
    'edges': [{'origin': 'c', 'target': 'e', 'negated': False}]
}

suite = Suite(
    conditions=[Parameter(id='c', variable='the button',
                          condition='is pressed')],
    expected=[Parameter(id='e', variable='the system',
                        condition='shuts down')],
    cases=[{'c': True, 'e': True}, {'c': False, 'e': False}]
)
suite_serialized = {
    'conditions': [{'id': 'c', 'variable': 'the button',
                    'condition': 'is pressed'}],
    'expected': [{'id': 'e', 'variable': 'the system',
                  'condition': 'shuts down'}],
    'cases': [{'c': True, 'e': True}, {'c': False, 'e': False}]
}


@pytest.fixture(scope="module")
@patch('src.api.service.CiRAConverter', autospec=True)
def isolatedService(converter) -> CiRAServiceImpl:
    # mock the CiRAConverter to isolate the system under test from it
    mockedConverter = mock.MagicMock()
    mockedConverter.classify.return_value = classification
    mockedConverter.label.return_value = labels
    mockedConverter.graph.return_value = graph
    mockedConverter.testsuite.return_value = suite

    # plug the mocked converter into the SUT
    converter.return_value = mockedConverter
    service = CiRAServiceImpl(model_classification=None, model_labeling=None)
    return service


@pytest.mark.unit
def test_classify(isolatedService):
    classification = isolatedService.classify(sentence)
    assert classification == classification


@pytest.mark.unit
def test_sentence_to_labels(isolatedService):
    labels = isolatedService.sentence_to_labels(sentence)
    assert labels == labels_serialized


@pytest.mark.unit
def test_sentence_to_graph_unlabeled(isolatedService):
    graph = isolatedService.sentence_to_graph(sentence, labels=None)
    assert graph == graph_serialized


@pytest.mark.unit
def test_sentence_to_graph_original_labels(isolatedService):
    graph = isolatedService.sentence_to_graph(
        sentence, labels=labels)
    assert graph == graph_serialized


@pytest.mark.unit
def test_sentence_to_graph_serialized_labels(isolatedService):
    graph = isolatedService.sentence_to_graph(
        sentence, labels=labels_serialized)
    assert graph == graph_serialized


@pytest.mark.unit
def test_graph_to_test_Graph(isolatedService):
    generated_suite = isolatedService.graph_to_test(graph=graph)
    assert generated_suite == suite_serialized


@pytest.mark.unit
def test_graph_to_test_dictgraph(isolatedService):
    generated_suite = isolatedService.graph_to_test(graph=graph_serialized)
    assert generated_suite == suite_serialized
