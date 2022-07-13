import pytest

from src.converters.labelstograph.graphconverter import GraphConverter
from src.converters.labelstograph.eventresolver import SimpleResolver

from src.util.loader import load_sentence

SENTENCES_PATH = './test/static/sentences'
LABELS_EVENT = ['Cause1', 'Cause2', 'Cause3', 'Effect1', 'Effect2', 'Effect3']
LABELS_SUB = ['Conjunction', 'Disjunction', 'Variable', 'Condition', 'Negation']

@pytest.fixture
def sut() -> GraphConverter:
    return GraphConverter(eventresolver=SimpleResolver())

@pytest.fixture
def sentence(id: str):
    _, sentence, labels, graph = load_sentence(filename=f'{SENTENCES_PATH}/sentence{id}.json')
    return {
        'text': sentence,
        'labels': labels,
        'graph': graph
    }

# currently excluded: sentence 16 (split cause1), 10 & 11 (for exceptive clauses), 17 (overruled precedence)
@pytest.mark.parametrize('id', ['1', '1b', '1c', '2', '3', '4', '5', '6', '6b', '7', '8', '12', '13', '14'])
def test_graphconverter(sentence, sut: GraphConverter):
    graph = sut.generate_graph(sentence['text'], sentence['labels'])
    assert sentence['graph'] == graph
