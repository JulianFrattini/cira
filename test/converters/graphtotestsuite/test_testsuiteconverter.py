import pytest

from src.converters.graphtotestsuite.testsuiteconverter import convert

from src.util.loader import load_sentence
import src.util.constants as constants

from src.data.test import Suite

@pytest.fixture
def sentence(id: str):
    _, _, _, graph, testsuite = load_sentence(filename=f'{constants.SENTENCES_PATH}/sentence{id}.json')
    return {
        'graph': graph,
        'testsuite': testsuite
    }

@pytest.mark.system
@pytest.mark.parametrize('id', ['1', '1b', '1c', '2', '3', '4', '5', '6', '6b', '7', '8', '10', '12', '13', '14', '16', '17'])
def test_system(sentence):
    """Automatically generate a test suite from a graph and compare it to a manually generated one."""
    testsuite: Suite = convert(sentence['graph'])
    assert testsuite == sentence['testsuite']
