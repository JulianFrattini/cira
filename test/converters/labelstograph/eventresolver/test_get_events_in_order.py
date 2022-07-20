import pytest

from src.converters.labelstograph.eventresolver import get_events_in_order

from src.data.labels import EventLabel

@pytest.fixture
def events() -> list[EventLabel]:
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
def test_L2_variable(events):
    candidates = get_events_in_order(label=events[1], attribute='Variable')
    assert [c.id for c in candidates] == ['L1', 'L3', 'L4', 'L5', 'L6']


@pytest.mark.integration
def test_L4_condition(events):
    candidates = get_events_in_order(label=events[3], attribute='Condition')
    assert [c.id for c in candidates] == ['L5', 'L6', 'L3', 'L2', 'L1']