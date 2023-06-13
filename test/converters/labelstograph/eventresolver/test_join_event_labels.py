import pytest

from src.converters.labelstograph.eventresolver import join_event_labels

from src.data.labels import EventLabel

@pytest.mark.unit
def test_no_join():
    c1 = EventLabel(id='e1', name='Cause1', begin=0, end=1)
    c2 = EventLabel(id='e2', name='Cause2', begin=2, end=3)
    e1 = EventLabel(id='e3', name='Effect1', begin=4, end=5)

    c1.set_successor(c2, junctor='AND')
    c2.set_successor(e1, junctor=None)

    event_labels: list[EventLabel] = [c1, c2, e1]

    result = join_event_labels(event_labels=event_labels)
    expected_result = [[c1], [c2], [e1]]

    assert result == expected_result

@pytest.mark.unit
def test_join():
    c1_1 = EventLabel(id='e1', name='Cause1', begin=0, end=1)
    c1_2 = EventLabel(id='e2', name='Cause1', begin=2, end=3)
    e1 = EventLabel(id='e3', name='Effect1', begin=4, end=5)

    c1_1.set_successor(c1_2, junctor=None)
    c1_2.set_successor(e1, junctor=None)

    event_labels: list[EventLabel] = [c1_1, c1_2, e1]

    result = join_event_labels(event_labels=event_labels)
    expected_result = [[c1_1, c1_2], [e1]]

    assert result == expected_result