import pytest

from src.data.graph import permute_configurations

@pytest.mark.unit
def test_permute_none():
    # if only one set of configurations is given, there is no need for permutation
    configurations = [[{'n1': True, 'n2': False}, {'n1': False, 'n2': True}]]
    permutations = permute_configurations(inc_configs=configurations)

    assert permutations == configurations[0]

@pytest.mark.unit
def test_permute_one():
    # if there are two sets of configurations, but one is just a singular configuration, add this configuration to the other ones
    configurations = [[{'n1': True, 'n2': False}, {'n1': False, 'n2': True}], [{'n3': True}]]
    permutations = permute_configurations(inc_configs=configurations)

    assert permutations == [{'n1': True, 'n2': False, 'n3': True}, {'n1': False, 'n2': True, 'n3': True}]

@pytest.mark.unit
def test_permute_two():
    # if there are two sets of configurations, with at least two configurations, expect the product of these configurations
    configurations = [[{'n1': True, 'n2': False}, {'n1': False, 'n2': True}], [{'n3': True}, {'n3': False}]]
    permutations = permute_configurations(inc_configs=configurations)

    # TODO this equality is dependent on the order of the elements in the list. Improve the ==
    assert permutations == [{'n1': True, 'n2': False, 'n3': True}, {'n1': True, 'n2': False, 'n3': False}, {'n1': False, 'n2': True, 'n3': True}, {'n1': False, 'n2': True, 'n3': False}]