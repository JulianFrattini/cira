import pytest

from src.data.graph import Graph, EventNode, IntermediateNode

@pytest.mark.unit
def test_graph_simple():
    c = EventNode(id='c1', variable='cause', condition='occurs')
    e = EventNode(id='e1', variable='event', condition='happens')
    edge = e.add_incoming(c)
    graph = Graph(nodes=[c, e], root=c, edges=[edge])
    serialized = graph.to_dict()
    
    expected = {
        'nodes': [
            {'id': 'c1', 'variable': 'cause', 'condition': 'occurs'},
            {'id': 'e1', 'variable': 'event', 'condition': 'happens'}
        ],
        'root': 'c1',
        'edges': [
            {'origin': 'c1', 'target': 'e1', 'negated': False}
        ]
    }
    assert serialized == expected

@pytest.mark.unit
def test_graph_negation():
    c = EventNode(id='c1', variable='cause', condition='occurs')
    e = EventNode(id='e1', variable='event', condition='happens')
    edge = e.add_incoming(c, negated=True)
    graph = Graph(nodes=[c, e], root=c, edges=[edge])
    serialized = graph.to_dict()
    
    expected = {
        'nodes': [
            {'id': 'c1', 'variable': 'cause', 'condition': 'occurs'},
            {'id': 'e1', 'variable': 'event', 'condition': 'happens'}
        ],
        'root': 'c1',
        'edges': [
            {'origin': 'c1', 'target': 'e1', 'negated': True}
        ]
    }
    assert serialized == expected

@pytest.mark.unit
def test_graph_multicause():
    c1 = EventNode(id='c1', variable='cause1', condition='occurs')
    c2 = EventNode(id='c2', variable='cause2', condition='occurs')
    i = IntermediateNode(id='i1', conjunction=False)
    e = EventNode(id='e1', variable='event', condition='happens')
    
    edges = []
    edges.append(i.add_incoming(c1))
    edges.append(i.add_incoming(c2))
    edges.append(e.add_incoming(i))
    graph = Graph(nodes=[c1, c2, i, e], root=i, edges=edges)
    serialized = graph.to_dict()
    
    expected = {
        'nodes': [
            {'id': 'c1', 'variable': 'cause1', 'condition': 'occurs'},
            {'id': 'c2', 'variable': 'cause2', 'condition': 'occurs'},
            {'id': 'i1', 'conjunction': False, 'precedence': False},
            {'id': 'e1', 'variable': 'event', 'condition': 'happens'}
        ],
        'root': 'i1',
        'edges': [
            {'origin': 'c1', 'target': 'i1', 'negated': False}, 
            {'origin': 'c2', 'target': 'i1', 'negated': False},
            {'origin': 'i1', 'target': 'e1', 'negated': False}
        ]
    }
    assert serialized == expected

@pytest.mark.unit
def test_graph_multieffect():
    c = EventNode(id='c1', variable='cause', condition='occurs')
    e1 = EventNode(id='e1', variable='event1', condition='happens')
    e2 = EventNode(id='e2', variable='event2', condition='happens')
    
    edges = []
    edges.append(e1.add_incoming(c))
    edges.append(e2.add_incoming(c))
    graph = Graph(nodes=[c, e1, e2], root=c, edges=edges)
    serialized = graph.to_dict()
    
    expected = {
        'nodes': [
            {'id': 'c1', 'variable': 'cause', 'condition': 'occurs'},
            {'id': 'e1', 'variable': 'event1', 'condition': 'happens'},
            {'id': 'e2', 'variable': 'event2', 'condition': 'happens'}
        ],
        'root': 'c1',
        'edges': [
            {'origin': 'c1', 'target': 'e1', 'negated': False}, 
            {'origin': 'c1', 'target': 'e2', 'negated': False}
        ]
    }
    assert serialized == expected

@pytest.mark.unit
def test_graph_multi():
    c1 = EventNode(id='c1', variable='cause1', condition='occurs')
    c2 = EventNode(id='c2', variable='cause2', condition='occurs')
    i = IntermediateNode(id='i1', conjunction=False)
    e1 = EventNode(id='e1', variable='event1', condition='happens')
    e2 = EventNode(id='e2', variable='event2', condition='happens')
    
    edges = []
    edges.append(i.add_incoming(c1, negated=True))
    edges.append(i.add_incoming(c2))
    edges.append(e1.add_incoming(i))
    edges.append(e2.add_incoming(i, negated=True))
    graph = Graph(nodes=[c1, c2, i, e1, e2], root=i, edges=edges)
    serialized = graph.to_dict()
    
    expected = {
        'nodes': [
            {'id': 'c1', 'variable': 'cause1', 'condition': 'occurs'},
            {'id': 'c2', 'variable': 'cause2', 'condition': 'occurs'},
            {'id': 'i1', 'conjunction': False, 'precedence': False},
            {'id': 'e1', 'variable': 'event1', 'condition': 'happens'},
            {'id': 'e2', 'variable': 'event2', 'condition': 'happens'}
        ],
        'root': 'i1',
        'edges': [
            {'origin': 'c1', 'target': 'i1', 'negated': True}, 
            {'origin': 'c2', 'target': 'i1', 'negated': False},
            {'origin': 'i1', 'target': 'e1', 'negated': False},
            {'origin': 'i1', 'target': 'e2', 'negated': True}
        ]
    }
    assert serialized == expected