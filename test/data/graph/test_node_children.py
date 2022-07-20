import pytest

from src.data.graph import IntermediateNode, EventNode
from src.data.labels import EventLabel, SubLabel

@pytest.mark.unit
def test_addchild():
    i = IntermediateNode(id='I1', conjunction=False)
    e = EventNode(id='E1')

    i.add_incoming(e)
    assert e.outgoing[0].target == i

@pytest.mark.unit
def test_removechild():
    i = IntermediateNode(id='I1', conjunction=False)
    e = EventNode(id='E1')
    i.add_incoming(e)

    i.remove_incoming(e)
    assert len(e.outgoing) == 0

@pytest.mark.unit
def test_addchildren():
    i = IntermediateNode(id='I1', conjunction=False)
    e1 = EventNode(id='E1')
    e2 = EventNode(id='E2')

    i.add_incoming(e1)
    i.add_incoming(e2)

    assert len(i.incoming) == 2

@pytest.mark.unit
def test_removeonechild():
    i = IntermediateNode(id='I1', conjunction=False)
    e1 = EventNode(id='E1')
    e2 = EventNode(id='E2')

    i.add_incoming(e1)
    i.add_incoming(e2)

    i.remove_incoming(e1)

    assert len(i.incoming) == 1

@pytest.mark.unit
def test_negatednode():
    l1 = EventLabel(id='L1', name='Cause1', begin=0, end=10)
    l1.add_child(SubLabel(id='L2', name='Negation', begin=0, end=2))
    e1 = EventNode(id='E1', label=l1)

    assert e1.is_negated() == True