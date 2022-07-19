import pytest, json

from src.util.loader import load_sentence

from src.data.graph import Graph, Node

SENTENCES_PATH = './test/static/sentences'

@pytest.fixture
def sentence(id: str) -> dict:
    """Load a static sentence from the repository of sentences.
    
    parameters:
        id -- unique id of a sentence file
        
    returns: dictionary containing the verbatim sentence, the manually generated graph, and the manually generated input configurations"""

    # load a static sentence
    file, sentence, _, graph, _ = load_sentence(f'{SENTENCES_PATH}/sentence{id}.json')

    # generate the input configurations from the testsuite 
    testsuite = file['testsuite']
    input_params: list = {param['id']:param['text'] for param in testsuite['inputparams']}
    configurations = []
    for tc in testsuite['testcases']:
        configuration = {f'[{input_params[config["inputid"]]}].({(config["text"] if not config["text"].startswith("not ") else config["text"][4:])})': not config['text'].startswith('not ') for config in tc['configurations']}
        configurations.append(configuration)

    return {
        'sentence': sentence,
        'graph': graph,
        'configurations': configurations
    }

# exclude sentence 11 (exceptive clause not supported yet)
@pytest.mark.parametrize('id', ['1', '1b', '1c', '2', '3', '4', '5', '6', '6b', '7', '8', '10', '12', '13', '14', '16', '17'])
def test_input_config_generation(sentence):
    """For the manually annotated, static sentences check that the get_testcase_configuration method generates the expected set of configurations of parameters to evaluate the root cause node of a graph to both True and False. The set is supposed to be minimal (as opposed to a brute force 2^len(events) test cases)."""

    graph: Graph = sentence['graph']

    # determine the configurations of input parameters such that the root node is evaluated to both true and false
    configurations = graph.root.get_testcase_configuration(expected_outcome=True) + \
        graph.root.get_testcase_configuration(expected_outcome=False)

    # replace the ids of the nodes in the configuration with verbatim nodes [variable].(condition) to make them comparable
    configs_verbatim = [{str(graph.get_node(id)): config[id] for id in config} for config in configurations]

    assert equal_configurations(manual_configurations=sentence['configurations'], generated_configurations=configs_verbatim)

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
        equivalent = [gconf for gconf in generated_configurations if gconf == mconf]
        if len(equivalent) != 1:
            return False
    
    return True