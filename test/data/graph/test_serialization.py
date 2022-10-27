import pytest

from src.data.graph import Graph, EventNode

@pytest.mark.unit
def test_graph1():
    c = EventNode(id='c1')
    e = EventNode(id='e1')
    edge = e.add_incoming(c)

    g = Graph(nodes=[c, e], root=c, edges=[edge])
    print(g.to_dict())

    assert True