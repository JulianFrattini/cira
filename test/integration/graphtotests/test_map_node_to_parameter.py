import pytest

from src.converters.graphtotestsuite.testsuiteconverter import map_node_to_parameter as mntp
from src.converters.graphtotestsuite.testsuiteconverter import generate_parameters as gp
from src.converters.graphtotestsuite.testsuiteconverter import get_expected_outcome as geo

from src.data.graph import EventNode



@pytest.mark.integration
@pytest.mark.parametrize('effect_edges_negated', [[False], [True], [False, False], [False, True], [True, False], [True, True]])
def test_test(effect_edges_negated):
    root = EventNode(id='C1', variable='the developer', condition='does not pey attention')

    events = []
    for index, effect_edge in enumerate(effect_edges_negated):
        effect = EventNode(id=f'E{index}', variable=f'effect {index}', condition='occurs')
        effect.add_incoming(child=root, negated=(effect_edge))
        events.append(effect)

    parameters = gp(nodes=events)
    expected_outcome = geo(root_node_evaluation=True, effects=events)
    configuration = mntp(configuration=expected_outcome, parameters_map=parameters)

    # construct the expected value
    expected = {f'P{index}': not ee for index, ee in enumerate(effect_edges_negated)}

    assert configuration == expected