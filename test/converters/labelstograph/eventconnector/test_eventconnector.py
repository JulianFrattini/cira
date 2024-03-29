import pytest
from unittest.mock import patch

from src.converters.labelstograph.eventconnector import connect_events

from src.data.labels import EventLabel, SubLabel
from src.data.graph import EventNode, IntermediateNode

@pytest.mark.integration
def test_connection():
    sentence = 'If an error is present or the debugger is active and an exception is triggered'

    cause1 = EventLabel(id="T2", name="Cause1", begin=3, end=22)
    cause1var = SubLabel(id="T3", name="Variable", begin=3, end=11)
    cause1cond = SubLabel(id="T4", name="Condition", begin=12, end=22)
    cause1.add_child(cause1var)
    cause1.add_child(cause1cond)

    disj = SubLabel(id="T5", name="Disjunction", begin=23, end=25)
        
    cause2 = EventLabel(id="T6", name="Cause2", begin=26, end=48)
    cause2var = SubLabel(id="T7", name="Variable", begin=26, end=38)
    cause2cond = SubLabel(id="T8", name="Condition", begin=39, end=48)
    cause2.add_child(cause2var)
    cause2.add_child(cause2cond)
    cause1.set_successor(cause2, junctor='OR')
        
    conj = SubLabel(id="T9", name="Conjunction", begin=49, end=52)

    cause3 = EventLabel(id="T10", name="Cause3", begin=53, end=78)
    cause3var = SubLabel(id="T11", name="Variable", begin=53, end=65)
    cause3cond = SubLabel(id="T12", name="Condition", begin=66, end=78)
    cause3.add_child(cause3var)
    cause3.add_child(cause3cond)
    cause2.set_successor(cause3, junctor='AND')

    # Events
    event1 = EventNode(id='E1', labels=[cause1])
    event1.variable = 'an error'
    event1.condition = 'is present'
    event2 = EventNode(id='E2', labels=[cause2])
    event2.variable = 'the debugger'
    event2.condition = 'is active'
    event3 = EventNode(id='E3', labels=[cause3])
    event3.variable = 'an exception'
    event3.condition = 'is triggered'

    events = [event1, event2, event3]

    causes, _ = connect_events(events)

    # there should be 5 cause nodes: 3 event nodes + 2 intermediate nodes
    assert len(causes) == 5

    root: IntermediateNode = causes[0]
    assert root.conjunction == False

@pytest.mark.integration
@patch('src.converters.labelstograph.eventconnector.generate_initial_nodenet')
@patch('src.converters.labelstograph.eventconnector.get_junctors')
def test_connection_overruled_precedence(mock_gj, mock_gin):
    """Test the event connection in a scenario with overruled precedence (e.g., "If A and either B or C" which should resolve to (A && (B || C)). The root node should be the conjunction, because the precedence of the disjunction overrules the conjunction in this case."""

    cause1 = EventNode(id='c1', labels=None, variable="v1")
    cause2 = EventNode(id='c2', labels=None, variable="v2")
    cause3 = EventNode(id='c3', labels=None, variable="v3")

    edgelist = []
    i1 = IntermediateNode(id='i1', conjunction=True)
    edgelist.append(i1.add_incoming(cause1))
    edgelist.append(i1.add_incoming(cause2))
    i2 = IntermediateNode(id='i2', conjunction=False, precedence=True)
    edgelist.append(i2.add_incoming(cause2))
    edgelist.append(i2.add_incoming(cause3))
    
    mock_gj.return_value = None
    mock_gin.return_value = ([i1, i2], edgelist)

    nodes, edges = connect_events([cause1, cause2, cause3])
    root = nodes[0]

    # make sure the root node is an intermediate node
    assert type(root) == IntermediateNode
    root: IntermediateNode = root

    # assert that this intermediate node is the conjunction, not the disjunction
    assert root.conjunction == True
