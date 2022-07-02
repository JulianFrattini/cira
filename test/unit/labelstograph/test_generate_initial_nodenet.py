import pytest
from unittest.mock import patch

from src.converters.labelstograph.eventconnecter import generate_initial_nodenet as gin

from src.data.graph import EventNode, IntermediateNode
from data.labels import SubLabel

@pytest.mark.unit
@patch('src.converters.labelstograph.eventconnecter.EventNode.is_negated')
def test_two_conjunction(mock_isnegated):
    mock_isnegated.return_value == False
    events = [EventNode(id='E1'), EventNode(id='E2')]
    jm = {('E1', 'E2'): 'AND'}

    intermediates = gin(events=events, junctor_map=jm)

    assert len(intermediates) == 1
    assert len(intermediates[0].children) == 2
    assert intermediates[0].children[0].target == events[0]
    assert intermediates[0].children[1].target == events[1]


@pytest.mark.unit
@patch('src.converters.labelstograph.eventconnecter.EventNode.is_negated')
def test_two_negation(mock_isnegated):
    mock_isnegated.return_value == True
    events: list[EventNode] = [EventNode(id='E1'), EventNode(id='E2')]
    jm = {('E1', 'E2'): 'AND'}

    intermediates = gin(events=events, junctor_map=jm)
    print(intermediates[0].children)

    assert intermediates[0].children[0].negated == True
    assert intermediates[0].children[1].negated == True

@pytest.mark.unit
@patch('src.converters.labelstograph.eventconnecter.EventNode.is_negated')
def test_three_conj_disj(mock_isnegated):
    mock_isnegated.return_value == False
    events = [EventNode(id='E1'), EventNode(id='E2'), EventNode(id='E3')]
    jm = {('E1', 'E2'): 'AND', ('E2', 'E3'): 'OR'}

    intermediates = gin(events=events, junctor_map=jm)
    
    assert len(intermediates) == 2
    assert len(intermediates[0].children) == 2
    assert intermediates[0].conjunction == True
    assert len(intermediates[1].children) == 2
    assert intermediates[1].conjunction == False
    assert intermediates[0].children[0].target == events[0]
    assert intermediates[0].children[1].target == events[1]
    assert intermediates[1].children[0].target == events[1]
    assert intermediates[1].children[1].target == events[2]