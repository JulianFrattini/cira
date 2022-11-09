import pytest

from src.util.loader import load_sentence
from src.util import constants

from src.data.graph import Graph
from src.data.test import Suite


@pytest.fixture
def sentence(id: str) -> dict:
    """Load a static sentence from the repository of sentences.

    parameters:
        id -- unique id of a sentence file

    returns: dictionary containing the verbatim sentence, the manually generated graph, and the manually generated input configurations"""

    _, _, _, graph, testsuite = load_sentence(
        f'{constants.SENTENCES_PATH}/sentence-{id}.json')

    configurations = generate_configurations(testsuite)

    return {
        'graph': graph,
        'configurations': configurations
    }


def generate_configurations(testsuite: Suite) -> list[dict]:
    """Generate a list of input-configuration mappings. Each test suite contains input parameters ("conditions") and output parameters ("expected"). Each test case within a test suite maps all input parameters to a boolean value. This method generates the mappings of all input parameters to their respective values for each test case in the test suite. 

    example: the sentence "If the button is pressed then the system shuts down." contains one input parameter (the button), one output parameter (the system), and two test cases (button is pressed and button is not pressed). This method hence generates the following configurations: [{'[the button].(is pressed)': True}, {'[the button].(is pressed)': False}]

    parameters: 
        testsuite -- the test suite to generate the configurations from

    returns: a list of dictionaries mapping verbatim parameters to their boolean configuration value
    """
    configurations = []
    ids_of_conditions = [parameter.id for parameter in testsuite.conditions]
    for tc in testsuite.cases:
        configuration = {f'[{testsuite.get_parameter(pid).variable}].({testsuite.get_parameter(pid).condition})': tc[pid]
                         for pid in tc if pid in ids_of_conditions}
        configurations.append(configuration)
    return configurations

# exclude sentence 11 (exceptive clause not supported yet)
@pytest.mark.integration
@pytest.mark.parametrize('id', ['1', '1b', '1c', '2', '3', '4', '5', '6', '6b', '7', '8', '10', '12', '13', '14', '16', '17'])
def test_input_config_generation(sentence):
    """For the manually annotated, static sentences check that the get_testcase_configuration method generates the expected set of configurations of parameters to evaluate the root cause node of a graph to both True and False. The set is supposed to be minimal (as opposed to a brute force 2^len(events) test cases)."""

    graph: Graph = sentence['graph']

    configurations = graph.root.get_testcase_configuration(expected_outcome=True) + \
        graph.root.get_testcase_configuration(expected_outcome=False)
    configurations_with_literal_nodes = [{str(graph.get_node(id)): config[id]
                                          for id in config} for config in configurations]

    assert equal_configurations(
        manual_configurations=sentence['configurations'], generated_configurations=configurations_with_literal_nodes)


def equal_configurations(manual_configurations: list[dict], generated_configurations: list[dict]) -> bool:
    """Check that two lists of configurations for input parameters {parameter: True/False} are equal.

    parameters:
        manual_configurations: list of manually generated configurations
        generated_configurations: list of automatically generated configurations

    returns: True, if for every manual configuration there is exactly one equal counterpart in the list of manual configurations
    """
    if len(manual_configurations) != len(generated_configurations):
        return False

    for mconf in manual_configurations:
        equivalent_configurations = [
            gconf for gconf in generated_configurations if gconf == mconf]
        if len(equivalent_configurations) != 1:
            return False

    return True
