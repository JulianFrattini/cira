from data.labels import EventLabel, SubLabel
import pytest

from src.data.graph import Node, IntermediateNode, EventNode

@pytest.mark.unit
def test_addchild():
    i = IntermediateNode(id='I1', conjunction=False)
    e = EventNode(id='E1')

    i.add_child(e)
    assert e.parents[0].origin == i

@pytest.mark.unit
def test_removechild():
    i = IntermediateNode(id='I1', conjunction=False)
    e = EventNode(id='E1')
    i.add_child(e)

    i.remove_child(e)
    assert len(e.parents) == 0

@pytest.mark.unit
def test_addchildren():
    i = IntermediateNode(id='I1', conjunction=False)
    e1 = EventNode(id='E1')
    e2 = EventNode(id='E2')

    i.add_child(e1)
    i.add_child(e2)

    assert len(i.children) == 2

@pytest.mark.unit
def test_removeonechild():
    i = IntermediateNode(id='I1', conjunction=False)
    e1 = EventNode(id='E1')
    e2 = EventNode(id='E2')

    i.add_child(e1)
    i.add_child(e2)

    i.remove_child(e1)

    assert len(i.children) == 1

@pytest.mark.unit
def test_negatednode():
    l1 = EventLabel(id='L1', name='Cause1', begin=0, end=10)
    l1.add_child(SubLabel(id='L2', name='Negation', begin=0, end=2))
    e1 = EventNode(id='E1', label=l1)

    assert e1.is_negated() == True