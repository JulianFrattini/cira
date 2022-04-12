import pytest

from src.converter2.util.graph import Node, EventNode, IntermediateNode

@pytest.mark.unit
def test_rewire():
    e1 = EventNode(variable='event1')
    e2 = EventNode(variable='event2')
    e3 = EventNode(variable='event3')

    i1 = IntermediateNode(conjunction=True, children=[e1, e2])
    i2 = IntermediateNode(conjunction=False, children=[e2, e3])

    i2.rewire(origin=e2, target=i1)

    parents = e2.getParents()
    assert len(parents) == 1
    assert parents[0] == i1
