import pytest

from src.data.graph import Graph, EventNode, IntermediateNode

@pytest.mark.integration
def test_simple():
    edgelist = []
    event1 = EventNode(id='E1', variable='the red button', condition = 'is pushed')
    event2 = EventNode(id='E2', variable = 'the blue button', condition = 'is released')

    junctor = IntermediateNode(id='E3', conjunction=False)
    edgelist.append(junctor.add_incoming(child=event1, negated=False))
    edgelist.append(junctor.add_incoming(child=event2, negated=False))

    event3 = EventNode(id='E3', variable = 'the system', condition = 'will shut down')
    edgelist.append(event3.add_incoming(child=junctor, negated=False))

    graph1 = Graph(nodes=[event1, event2, junctor, event3], root=junctor, edges=edgelist)
    assert graph1 == graph1

@pytest.mark.integration
def test_switched_node_order():
    edgelist1 = []
    event1 = EventNode(id='E1', variable = 'the red button', condition = 'is pushed')
    event2 = EventNode(id='E2', variable = 'the blue button', condition = 'is released')

    junctor1 = IntermediateNode(id='E3', conjunction=False)
    edgelist1.append(junctor1.add_incoming(child=event1, negated=False))
    edgelist1.append(junctor1.add_incoming(child=event2, negated=False))

    event3 = EventNode(id='E3', variable = 'the system', condition = 'will shut down')
    edgelist1.append(event3.add_incoming(child=junctor1, negated=False))

    graph1 = Graph(nodes=[event1, event2, junctor1, event3], root=junctor1, edges=edgelist1)

    edgelist2 = []
    event21 = EventNode(id='E1', variable = 'the red button', condition = 'is pushed')
    event22 = EventNode(id='E2', variable = 'the blue button', condition = 'is released')

    junctor2 = IntermediateNode(id='E3', conjunction=False)
    edgelist2.append(junctor2.add_incoming(child=event22, negated=False))
    edgelist2.append(junctor2.add_incoming(child=event21, negated=False))

    event23 = EventNode(id='E3', variable = 'the system', condition = 'will shut down')
    edgelist2.append(event23.add_incoming(child=junctor2, negated=False))

    graph2 = Graph(nodes=[event21, event22, junctor2, event23], root=junctor2, edges=edgelist2)
    assert graph1 == graph2

@pytest.mark.integration
def test_inequal_number_of_effects():
    # graph 1
    root = EventNode(id='c1', label=None, variable='an error', condition='occurs')
    effect1 = EventNode(id='e1', variable='a message', condition='is shown')
    effect1.add_incoming(child=root, negated=False)
    graph1 = Graph(nodes=[root, effect1], root=root, edges=None)

    # graph 2
    root = EventNode(id='c1', label=None, variable='an error', condition='occurs')
    effect1 = EventNode(id='e1', variable='a message', condition='is shown')
    effect2 = EventNode(id='e2', variable='a sound', condition='is played')
    effect1.add_incoming(child=root)
    effect2.add_incoming(child=root)
    graph2 = Graph(nodes=[root, effect1, effect2], root=root, edges=None)

    assert graph1 != graph2

@pytest.mark.integration
def test_inequal_effects_variable():
    # graph 1
    root1 = EventNode(id='c1', label=None, variable='an error', condition='occurs')
    effect1 = EventNode(id='e1', variable='a message', condition='is shown')
    effect1.add_incoming(child=root1, negated=False)
    graph1 = Graph(nodes=[root1, effect1], root=root1, edges=None)

    # graph 2: the variable of the effect node is different
    root2 = EventNode(id='c1', label=None, variable='an error', condition='occurs')
    effect2 = EventNode(id='e1', variable='the message', condition='is shown')
    effect2.add_incoming(child=root2)
    graph2 = Graph(nodes=[root2, effect1], root=root2, edges=None)

    assert graph1 != graph2

@pytest.mark.integration
def test_inequal_effects_condition():
    # graph 1
    root1 = EventNode(id='c1', label=None, variable='an error', condition='occurs')
    effect1 = EventNode(id='e1', variable='a message', condition='is shown')
    effect1.add_incoming(child=root1, negated=False)
    graph1 = Graph(nodes=[root1, effect1], root=root1, edges=None)

    # graph 2: the variable of the effect node is different
    root2 = EventNode(id='c1', label=None, variable='an error', condition='occurs')
    effect2 = EventNode(id='e1', variable='a message', condition='is opened')
    effect2.add_incoming(child=root2)
    graph2 = Graph(nodes=[root2, effect1], root=root2, edges=None)

    assert graph1 != graph2

@pytest.mark.integration
def test_inequal_effects_negation():
    # graph 1
    root1 = EventNode(id='c1', label=None, variable='an error', condition='occurs')
    effect1 = EventNode(id='e1', variable='a message', condition='is shown')
    effect1.add_incoming(child=root1, negated=False)
    graph1 = Graph(nodes=[root1, effect1], root=root1, edges=None)

    # graph 2: the variable of the effect node is different
    root2 = EventNode(id='c1', label=None, variable='an error', condition='occurs')
    effect2 = EventNode(id='e1', variable='a message', condition='is shown')
    effect2.add_incoming(child=root2, negated=True)
    graph2 = Graph(nodes=[root2, effect1], root=root2, edges=None)

    assert graph1 != graph2