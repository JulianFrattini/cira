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

@pytest.mark.integration
def test_connect_neighbors():
    c1 = EventLabel(id='T1', name='Cause1', begin=0, end=5)
    c2 = EventLabel(id='T2', name='Cause2', begin=6, end=10)
    e1 = EventLabel(id='T4', name='Effect1', begin=11, end=20)
    labels = [c2, e1, c1]

    connect_labels(labels)

    assert c1.predecessor == None
    assert c1.successor.target == c2
    assert c2.predecessor.origin == c1
    assert c2.successor.target == e1
    assert e1.predecessor.origin == c2
    assert e1.successor == None

@pytest.mark.integration
def test_junctors():
    c1 = EventLabel(id='T1', name='Cause1', begin=0, end=5)
    conj = SubLabel(id='T2', name='Conjunction', begin=6, end=9)
    c2 = EventLabel(id='T3', name='Cause2', begin=10, end=15)
    disj = SubLabel(id='T4', name='Disjunction', begin=16, end=18)
    c3 = EventLabel(id='T5', name='Cause2', begin=19, end=24)
    c4 = EventLabel(id='T5', name='Cause2', begin=25, end=30)
    labels = [c1, conj, c2, disj, c3, c4]

    connect_labels(labels)

    assert c1.successor.junctor == 'AND'
    assert c2.successor.junctor == 'OR'
    assert c3.successor.junctor == None

@pytest.mark.integration
def test_junctors_overruled_precedence1():
    """Usually, we interpret junctors like logical operators and hence assume that AND has a higher precedence than OR. For example, "A or B and C" is interpreted as "A or (B and C)". However, the precedence can be overruled in a case like "A and either B or C", which is interpreted as "A and (B or C)". The indicator for the overruled precedence is the existence of both a conjunction and disjunction between two events
    """
    c1 = EventLabel(id='T1', name='Cause1', begin=0, end=5)
    # indicator for the overruled precedence: conjunction and disjunction between cause 1 and 2
    conj = SubLabel(id='T2-1', name='Conjunction', begin=6, end=7)
    disjp = SubLabel(id='T2-2', name='Disjunction', begin=8, end=9)
    c2 = EventLabel(id='T3', name='Cause2', begin=10, end=15)
    disj = SubLabel(id='T4', name='Disjunction', begin=16, end=18)
    c3 = EventLabel(id='T5', name='Cause2', begin=19, end=24)
    labels = [c1, conj, disjp, c2, disj, c3]

    connect_labels(labels)

    assert c1.successor.junctor == 'AND'
    assert c2.successor.junctor == 'POR'

#either A or B and C
@pytest.mark.integration
@pytest.mark.skip(reason="UNCLEAR_REQUIREMENT: how this case is to be resolved linguistically is not yet clear.")
def test_junctors_overruled_precedence2():
    """Another version of the overruled precedence is if the indicator for the overruling precedence (either) being in the beginning, e.g., "When either A or B and C." It is yet unclear how this case should be resolved."""

    disjp = SubLabel(id='T0', name='Disjunction', begin=8, end=9)
    c1 = EventLabel(id='T1', name='Cause1', begin=0, end=5)
    disj = SubLabel(id='T2', name='Disjunction', begin=6, end=7)
    c2 = EventLabel(id='T3', name='Cause2', begin=10, end=15)
    conj = SubLabel(id='T4', name='Conjunction', begin=16, end=18)
    c3 = EventLabel(id='T5', name='Cause2', begin=19, end=24)
    labels = [disjp, c1, disj, c2, conj, c3]

    connect_labels(labels)

    assert False