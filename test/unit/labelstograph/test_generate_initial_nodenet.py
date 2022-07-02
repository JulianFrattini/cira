import pytest

from src.converters.labelstograph.eventconnecter import generate_initial_nodenet as gin

from src.data.graph import EventNode, IntermediateNode

@pytest.mark.unit
def test_two_conjunction():
    events = [EventNode(id='E1'), EventNode(id='E2')]
    jm = {('E1', 'E2'): 'AND'}

    intermediates = gin(events=events, junctor_map=jm)

    i = IntermediateNode(id='I0', conjunction=True)
    i.add_children([events[0], events[1]])
    expected = [i]

    assert intermediates == expected

@pytest.mark.unit
def test_three_conj_disj():
    events = [EventNode(id='E1'), EventNode(id='E2'), EventNode(id='E3')]
    jm = {('E1', 'E2'): 'AND', ('E2', 'E3'): 'OR'}

    intermediates = gin(events=events, junctor_map=jm)

    # construct the expected value
    i1 = IntermediateNode(id='I0', conjunction=True)
    i1.add_children([events[0], events[1]])
    i2 = IntermediateNode(id='I1', conjunction=False)
    i2.add_children([events[1], events[2]])
    expected = [i1, i2]


    assert intermediates == expected

@pytest.mark.unit
def test_three_disj_conj():
    events = [EventNode(id='E1'), EventNode(id='E2'), EventNode(id='E3')]
    jm = {('E1', 'E2'): 'OR', ('E2', 'E3'): 'AND'}

    intermediates = gin(events=events, junctor_map=jm)

    # construct the expected value
    i1 = IntermediateNode(id='I0', conjunction=False)
    i1.add_children([events[0], events[1]])
    i2 = IntermediateNode(id='I1', conjunction=True)
    i2.add_children([events[1], events[2]])
    expected = [i1, i2]


    assert intermediates == expected