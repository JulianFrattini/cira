import pytest

from src.data.graph import EventNode, IntermediateNode

@pytest.mark.integration
def test_conjuction_disjunction():
    event = EventNode(id='e', labels=None)
    i1 = IntermediateNode(id='conj', conjunction=True)
    i2 = IntermediateNode(id='disj', conjunction=False)
    i1.add_incoming(event)
    i2.add_incoming(event)

    ordered_parents: list[IntermediateNode] = event.get_parents_ordered_by_precedence()

    assert len(ordered_parents) == 2
    assert ordered_parents[0].conjunction == False
    assert ordered_parents[1].conjunction == True

@pytest.mark.integration
def test_overruling_disjunction_conjunction():
    event = EventNode(id='e', labels=None)
    i1 = IntermediateNode(id='disj', conjunction=False, precedence=True)
    i2 = IntermediateNode(id='conj', conjunction=True)
    i1.add_incoming(event)
    i2.add_incoming(event)

    ordered_parents: list[IntermediateNode] = event.get_parents_ordered_by_precedence()

    assert len(ordered_parents) == 2
    assert ordered_parents[0].conjunction == True
    assert ordered_parents[1].conjunction == False