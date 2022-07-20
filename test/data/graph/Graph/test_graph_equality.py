import pytest

from src.data.graph import Graph, EventNode, IntermediateNode

@pytest.mark.integration
def test_simple():
    edgelist = []
    event1 = EventNode(id='E1')
    event1.variable = 'the red button'
    event1.condition = 'is pushed'

    event2 = EventNode(id='E2')
    event2.variable = 'the blue button'
    event2.condition = 'is released'

    junctor = IntermediateNode(id='E3', conjunction=False)
    edgelist.append(junctor.add_incoming(child=event1, negated=False))
    edgelist.append(junctor.add_incoming(child=event2, negated=False))

    event3 = EventNode(id='E3')
    event3.variable = 'the system'
    event3.condition = 'will shut down'
    edgelist.append(event3.add_incoming(child=junctor, negated=False))

    graph1 = Graph(nodes=[event1, event2, junctor, event3], root=junctor, edges=edgelist)
    assert graph1 == graph1

@pytest.mark.integration
def test_switched_node_order():
    edgelist1 = []
    event1 = EventNode(id='E1')
    event1.variable = 'the red button'
    event1.condition = 'is pushed'

    event2 = EventNode(id='E2')
    event2.variable = 'the blue button'
    event2.condition = 'is released'

    junctor1 = IntermediateNode(id='E3', conjunction=False)
    edgelist1.append(junctor1.add_incoming(child=event1, negated=False))
    edgelist1.append(junctor1.add_incoming(child=event2, negated=False))

    event3 = EventNode(id='E3')
    event3.variable = 'the system'
    event3.condition = 'will shut down'
    edgelist1.append(event3.add_incoming(child=junctor1, negated=False))

    graph1 = Graph(nodes=[event1, event2, junctor1, event3], root=junctor1, edges=edgelist1)

    edgelist2 = []
    event21 = EventNode(id='E1')
    event21.variable = 'the red button'
    event21.condition = 'is pushed'

    event22 = EventNode(id='E2')
    event22.variable = 'the blue button'
    event22.condition = 'is released'

    junctor2 = IntermediateNode(id='E3', conjunction=False)
    edgelist2.append(junctor2.add_incoming(child=event22, negated=False))
    edgelist2.append(junctor2.add_incoming(child=event21, negated=False))

    event23 = EventNode(id='E3')
    event23.variable = 'the system'
    event23.condition = 'will shut down'
    edgelist2.append(event23.add_incoming(child=junctor2, negated=False))

    graph2 = Graph(nodes=[event21, event22, junctor2, event23], root=junctor2, edges=edgelist2)
    assert graph1 == graph2