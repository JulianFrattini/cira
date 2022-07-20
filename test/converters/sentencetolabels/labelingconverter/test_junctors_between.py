import pytest

from src.data.labels import Label, EventLabel, SubLabel

from src.converters.sentencetolabels.labelingconverter import get_junctors_between

@pytest.mark.unit
def test_junctor_exist():
    labels: list[Label] = [
        EventLabel(id='L1', name='Cause1', begin=0, end=10),
        SubLabel(id='L2', name='Conjunction', begin=11, end=14),
        EventLabel(id='L3', name='Cause2', begin=15, end=25),
    ]

    junctors = get_junctors_between(labels=labels, first=labels[0], second=labels[2])
    assert junctors[0].name == 'Conjunction'

@pytest.mark.unit
def test_junctor_notexist():
    labels: list[Label] = [
        EventLabel(id='L1', name='Cause1', begin=0, end=10),
        EventLabel(id='L3', name='Cause2', begin=15, end=25),
    ]

    junctors = get_junctors_between(labels=labels, first=labels[0], second=labels[1])
    assert len(junctors) == 0

@pytest.mark.unit
def test_junctor_outside():
    labels: list[Label] = [
        EventLabel(id='L1', name='Cause1', begin=0, end=10),
        SubLabel(id='L2', name='Conjunction', begin=22, end=25),
        EventLabel(id='L3', name='Cause2', begin=11, end=21),
    ]

    junctors = get_junctors_between(labels=labels, first=labels[0], second=labels[2])
    assert len(junctors) == 0

@pytest.mark.unit
def test_junctor_two():
    labels: list[Label] = [
        EventLabel(id='L1', name='Cause1', begin=0, end=10),
        SubLabel(id='L2', name='Conjunction', begin=11, end=14),
        SubLabel(id='L3', name='Disjunction', begin=15, end=17),
        EventLabel(id='L4', name='Cause2', begin=18, end=28),
    ]

    junctors = get_junctors_between(labels=labels, first=labels[0], second=labels[3])
    assert len(junctors) == 2