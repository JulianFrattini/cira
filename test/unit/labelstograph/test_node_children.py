import pytest

from src.data.graph import Node, IntermediateNode, EventNode

@pytest.mark.unit
def test_addchild():
    i = IntermediateNode(id='I1', conjunction=False)
    e = EventNode(id='E1')

    i.add_children([e])

    assert e.parents[0] == i

@pytest.mark.unit
def test_removechild():
    i = IntermediateNode(id='I1', conjunction=False)
    e = EventNode(id='E1')
    i.add_children([e])

    i.remove_child(e)

    assert len(e.parents) == 0

@pytest.mark.unit
def test_addchildren():
    i = IntermediateNode(id='I1', conjunction=False)
    e1 = EventNode(id='E1')
    e2 = EventNode(id='E2')

    i.add_children([e1, e2])

    assert len(i.children) == 2

@pytest.mark.unit
def test_removeonechild():
    i = IntermediateNode(id='I1', conjunction=False)
    e1 = EventNode(id='E1')
    e2 = EventNode(id='E2')
    i.add_children([e1, e2])

    i.remove_child(e1)

    assert len(i.children) == 1