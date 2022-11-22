import pytest

from src.converters.labelstograph.eventresolver import get_events_in_order

from src.data.labels import EventLabel
from src.data.graph import EventNode

@pytest.fixture
def events_with_single_label() -> list[EventLabel]:
    c1 = EventLabel('L1', name='Cause1', begin=0, end=1)
    c2 = EventLabel('L2', name='Cause2', begin=1, end=2)
    c3 = EventLabel('L3', name='Cause3', begin=2, end=3)
    e1 = EventLabel('L4', name='Effect1', begin=3, end=4)
    e2 = EventLabel('L5', name='Effect2', begin=4, end=5)
    e3 = EventLabel('L6', name='Effect3', begin=5, end=6)

    c1.set_successor(c2, None)
    c2.set_successor(c3, None)
    c3.set_successor(e1, None)
    e1.set_successor(e2, None)
    e2.set_successor(e3, None)

    return [c1, c2, c3, e1, e2, e3]

@pytest.mark.integration
def test_L2_variable(events_with_single_label):
    node = EventNode(id='N1', labels=[events_with_single_label[1]])
    candidates = get_events_in_order(starting_node=node, attribute='Variable')
    assert [c.id for c in candidates] == ['L1', 'L3', 'L4', 'L5', 'L6']


@pytest.mark.integration
def test_L4_condition(events_with_single_label):
    node = EventNode(id='N1', labels=[events_with_single_label[3]])
    candidates = get_events_in_order(starting_node=node, attribute='Condition')
    assert [c.id for c in candidates] == ['L5', 'L6', 'L3', 'L2', 'L1']

@pytest.fixture
def events_with_multiple_label() -> list[EventLabel]:
    c1 = EventLabel('L1', name='Cause1', begin=0, end=1)
    c2_1 = EventLabel('L2-1', name='Cause2', begin=1, end=2)
    c2_2 = EventLabel('L2-2', name='Cause2', begin=2, end=3)
    c3 = EventLabel('L3', name='Cause3', begin=4, end=5)
    e1 = EventLabel('L4', name='Effect1', begin=5, end=6)
    e2_1 = EventLabel('L5-1', name='Effect2', begin=7, end=8)
    e2_2 = EventLabel('L5-2', name='Effect2', begin=8, end=9)
    e3 = EventLabel('L6', name='Effect3', begin=9, end=10)

    c1.set_successor(c2_1, None)
    c2_1.set_successor(c2_2, "MERGE")
    c2_2.set_successor(c3, None)
    c3.set_successor(e1, None)
    e1.set_successor(e2_1, None)
    e2_1.set_successor(e2_2, "MERGE")
    e2_2.set_successor(e3, None)

    return [c1, c2_1, c2_2, c3, e1, e2_1, e2_2, e3]

@pytest.mark.integration
def test_L2_1_variable(events_with_multiple_label):
    c2_1 = events_with_multiple_label[1]
    c2_2 = events_with_multiple_label[2]
    node = EventNode(id='N1', labels=[c2_1, c2_2])

    candidates = get_events_in_order(starting_node=node, attribute='Variable')
    assert [c.id for c in candidates] == ['L1', 'L3', 'L4', 'L5-1', 'L5-2', 'L6']