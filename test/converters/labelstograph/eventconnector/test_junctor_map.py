import pytest

from src.converters.labelstograph.eventconnector import get_junctors

from src.data.graph import EventNode
from src.data.labels import EventLabel

@pytest.mark.unit
def test_conjunction():
    c1 = EventLabel(id='L1', name='Cause1', begin=0, end=10)
    c2 = EventLabel(id='L2', name='Cause2', begin=15, end=20)
    c1.set_successor(successor=c2, junctor='AND')

    nodes = [EventNode(id='E1', label=c1), EventNode(id='E2', label=c2)]

    junctors = get_junctors(events=nodes)
    assert junctors[('E1', 'E2')] == 'AND'

@pytest.mark.unit
def test_disjunction():
    c1 = EventLabel(id='L1', name='Cause1', begin=0, end=10)
    c2 = EventLabel(id='L2', name='Cause2', begin=15, end=20)
    c1.set_successor(successor=c2, junctor='OR')

    nodes = [EventNode(id='E1', label=c1), EventNode(id='E2', label=c2)]

    junctors = get_junctors(events=nodes)
    assert junctors[('E1', 'E2')] == 'OR'

@pytest.mark.unit
def test_nojunction():
    c1 = EventLabel(id='L1', name='Cause1', begin=0, end=10)
    c2 = EventLabel(id='L2', name='Cause2', begin=15, end=20)
    c1.set_successor(successor=c2, junctor=None)

    nodes = [EventNode(id='E1', label=c1), EventNode(id='E2', label=c2)]

    # if no junctor is available at all, assume a conjunction
    junctors = get_junctors(events=nodes)
    assert junctors[('E1', 'E2')] == 'AND'

@pytest.mark.unit
def test_implicit_conjunction():
    c1 = EventLabel(id='L1', name='Cause1', begin=0, end=10)
    c2 = EventLabel(id='L2', name='Cause2', begin=15, end=20)
    c3 = EventLabel(id='L3', name='Cause3', begin=25, end=30)
    c1.set_successor(successor=c2, junctor=None)
    c2.set_successor(successor=c3, junctor='AND')

    nodes = [EventNode(id='E1', label=c1), EventNode(id='E2', label=c2), EventNode(id='E3', label=c3)]

    junctors = get_junctors(events=nodes)
    assert junctors[('E1', 'E2')] == 'AND'