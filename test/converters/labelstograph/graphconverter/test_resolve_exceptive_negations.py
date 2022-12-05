import pytest

from src.converters.labelstograph.graphconverter import resolve_exceptive_negations

from src.data.labels import EventLabel, SubLabel

@pytest.mark.integration
def test_exceptive_negation_found():
    labels = [
        SubLabel(id='L1', name='Negation', begin=0, end=6),
        EventLabel(id='L2', name='Cause1', begin=7, end=17)
    ]

    affected_labels = resolve_exceptive_negations(labels)

    expected = [labels[1]]
    assert affected_labels == expected

@pytest.mark.integration
def test_exceptive_negation_found_cascading():
    labels = [
        SubLabel(id='L1', name='Negation', begin=0, end=6),
        EventLabel(id='L2', name='Cause1', begin=7, end=17),
        EventLabel(id='L3', name='Cause2', begin=18, end=28)
    ]
    c1: EventLabel = labels[1]
    c1.set_successor(labels[2], "AND")

    affected_labels = resolve_exceptive_negations(labels)

    expected = [labels[1], labels[2]]
    assert affected_labels == expected

@pytest.mark.integration
def test_exceptive_negation_found_cascading_twice():
    labels = [
        SubLabel(id='L1', name='Negation', begin=0, end=6),
        EventLabel(id='L2', name='Cause1', begin=7, end=17),
        EventLabel(id='L3', name='Cause2', begin=18, end=28),
        EventLabel(id='L4', name='Cause3', begin=29, end=39)
    ]
    c1: EventLabel = labels[1]
    c2: EventLabel = labels[2]
    c1.set_successor(c2, "AND")
    c2.set_successor(labels[3], "AND")

    affected_labels = resolve_exceptive_negations(labels)

    expected = [labels[1], labels[2], labels[3]]
    assert affected_labels == expected

@pytest.mark.integration
def test_exceptive_negation_found_not_cascading():
    labels = [
        SubLabel(id='L1', name='Negation', begin=0, end=6),
        EventLabel(id='L2', name='Cause1', begin=7, end=17),
        EventLabel(id='L3', name='Cause2', begin=18, end=28)
    ]
    c1: EventLabel = labels[1]
    c1.set_successor(labels[2], "OR")

    affected_labels = resolve_exceptive_negations(labels)

    expected = [labels[1]]
    assert affected_labels == expected

@pytest.mark.integration
def test_exceptive_negation_found_cascading_stopped():
    labels = [
        SubLabel(id='L1', name='Negation', begin=0, end=6),
        EventLabel(id='L2', name='Cause1', begin=7, end=17),
        EventLabel(id='L3', name='Cause2', begin=18, end=28),
        EventLabel(id='L4', name='Cause3', begin=29, end=39)
    ]
    c1: EventLabel = labels[1]
    c2: EventLabel = labels[2]
    c1.set_successor(c2, "AND")
    c2.set_successor(labels[3], "OR")

    affected_labels = resolve_exceptive_negations(labels)

    expected = [labels[1], labels[2]]
    assert affected_labels == expected

@pytest.mark.integration
def test_exceptive_negation_found_cascading():
    labels = [
        SubLabel(id='L1', name='Negation', begin=0, end=6),
        EventLabel(id='L2', name='Cause1', begin=7, end=17),
        EventLabel(id='L3', name='Effect1', begin=18, end=28)
    ]
    c1: EventLabel = labels[1]
    c1.set_successor(labels[2], None)

    affected_labels = resolve_exceptive_negations(labels)

    expected = [labels[1]]
    assert affected_labels == expected

@pytest.mark.integration
def test_no_exceptive_negation_found():
    negation = SubLabel(id='L1', name='Negation', begin=0, end=6)
    event = EventLabel(id='L2', name='Cause1', begin=7, end=17)
    event.add_child(child=negation)
    labels = [negation, event]

    affected_labels = resolve_exceptive_negations(labels)
    assert affected_labels == []