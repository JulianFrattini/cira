import pytest
from typing import Tuple

from src.data.labels import Label, EventLabel, SubLabel
from src.converters.sentencetolabels.labelingconverter import connect_labels

@pytest.fixture
def two_labels(event: Tuple[int, int], variable: Tuple[int, int]) -> list[Label]:
    """Create a list of two labels (one event, one variable) with a given begin and end point
    
    parameters:
        event -- begin and end point of the event label
        variable -- begin and end point of the variable label

    returns: list of two labels with the given begin and end point
    """
    return [
        EventLabel(id='T1', name='Cause1', begin=event[0], end=event[1]),
        SubLabel(id='T2', name='Variable', begin=variable[0], end=variable[1])
    ]

@pytest.mark.integration
@pytest.mark.parametrize('event, variable, expected', [
    ((0, 5), (0, 3), 1), 
    ((0, 5), (3, 5), 1),
    ((0, 5), (0, 5), 1),
    ((1, 5), (0, 3), 0), 
    ((0, 4), (3, 5), 0),
    ])
def test_connect_childcount(two_labels, expected):
    """Test that connecting two labels with a given configuration of begin and end points results in the expected number of children
    
    parameters:
        two_labels -- fixture creating a list of two labels with the parametrized configuration
        expected -- number of children that the first label is supposed to have after the connection
    """
    connect_labels(two_labels)

    assert len(two_labels[0].children) == expected
    
    if expected == 1:
        assert two_labels[0].children[0] == two_labels[1]
        assert two_labels[1].parent == two_labels[0]