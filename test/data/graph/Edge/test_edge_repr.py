import pytest

from src.data.graph import Edge, EventNode

@pytest.mark.unit
def test_repr():
    n1 = EventNode(id='n1', labels=None, variable='node 1', condition='is present')
    n2 = EventNode(id='n2', labels=None, variable='node 2', condition='is active')
    e = Edge(origin=n1, target=n2)

    assert e.__repr__() == 'n1 ---> n2'

@pytest.mark.unit
def test_repr_negated():
    n1 = EventNode(id='n1', labels=None, variable='node 1', condition='is present')
    n2 = EventNode(id='n2', labels=None, variable='node 2', condition='is active')
    e = Edge(origin=n1, target=n2, negated=True)

    assert e.__repr__() == 'n1 -~-> n2'