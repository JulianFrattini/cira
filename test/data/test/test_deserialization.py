import pytest

from src.data.test import Suite, Parameter, from_dict

@pytest.mark.unit
def test_deserialization():
    suite_dict = {
        'conditions': [{'id': 'c', 'variable': 'cause', 'condition': 'occurs'}],
        'expected': [{'id': 'e', 'variable': 'effect', 'condition': 'happens'}],
        'cases': [
            {'c': False, 'e': False},
            {'c': True, 'e': True}
        ]
    }
    deserialized = from_dict(suite_dict)

    cause = Parameter(id='c', variable='cause', condition='occurs')
    effect = Parameter(id='e', variable='effect', condition='happens')
    cases=[
        {'c': False, 'e': False},
        {'c': True, 'e': True}
    ]
    expected = Suite(conditions=[cause], expected=[effect], cases=cases)

    assert deserialized == expected