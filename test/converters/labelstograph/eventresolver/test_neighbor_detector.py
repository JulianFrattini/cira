import pytest

from src.data.labels import EventLabel

from src.converters.labelstograph.eventresolver import get_all_neighbors_of_type as neighbors

@pytest.fixture
def events() -> list[EventLabel]:
    c1 = EventLabel('L1', name='Cause1', begin=0, end=1)
    c2 = EventLabel('L2', name='Cause2', begin=1, end=2)
    c3 = EventLabel('L3', name='Cause3', begin=2, end=3)
    e1 = EventLabel('L4', name='Effect1', begin=3, end=4)
    e2 = EventLabel('L5', name='Effect2', begin=4, end=5)
    e3 = EventLabel('L6', name='Effect3', begin=5, end=6)

    c1.set_successor(c2, junctor='AND')
    c2.set_successor(c3, junctor='AND')
    c3.set_successor(e1, junctor='AND')
    e1.set_successor(e2, junctor='AND')
    e2.set_successor(e3, junctor='AND')

    return [c1, c2, c3, e1, e2, e3]

@pytest.mark.unit
def test_preceeding_causes(events):
    candidates = neighbors(startlabel=events[1], direction='predecessor', type='Cause')

    assert len(candidates) == 1
    assert candidates[0] == events[0]

@pytest.mark.unit
def test_succeeding_causes(events):
    candidates = neighbors(startlabel=events[1], direction='successor', type='Cause')

    assert len(candidates) == 1
    assert candidates[0] == events[2]

@pytest.mark.unit
def test_preceeding_effects(events):
    candidates = neighbors(startlabel=events[1], direction='predecessor', type='Effect')

    assert len(candidates) == 0

@pytest.mark.unit
def test_succeeding_effects(events):
    candidates = neighbors(startlabel=events[1], direction='successor', type='Effect')

    assert len(candidates) == 3
    assert candidates[0] == events[3]
    assert candidates[1] == events[4]
    assert candidates[2] == events[5]