import pytest

from dataclasses import asdict
from src.data.test import Suite, Parameter

@pytest.mark.unit
def test_test():
    cause = Parameter(id='c', variable='cause', condition='occurs')
    effect = Parameter(id='e', variable='effect', condition='happens')
    cases=[
        {'c': False, 'e': False},
        {'c': True, 'e': True}
    ]
    suite = Suite(conditions=[cause], expected=[effect], cases=cases)
    serialized = asdict(suite)

    expected = {
        'conditions': [{'id': 'c', 'variable': 'cause', 'condition': 'occurs'}],
        'expected': [{'id': 'e', 'variable': 'effect', 'condition': 'happens'}],
        'cases': [
            {'c': False, 'e': False},
            {'c': True, 'e': True}
        ]
    }
    assert serialized == expected