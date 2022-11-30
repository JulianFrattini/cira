import pytest

from src.converters.sentencetolabels.labelrecovery import label_exceptive_clauses

from src.data.labels import Label, EventLabel, SubLabel

@pytest.mark.integration
def test_missing():
    sentence = "Unless the button is pressed."
    labels = [
        SubLabel(id='L1', name='Variable', begin=7, end=17),
        SubLabel(id='L2', name='Condition', begin=18, end=28),
        EventLabel(id='L3', name='Cause1', begin=7, end=28)
    ]

    additional_labels = label_exceptive_clauses(sentence, labels)

    expected = [SubLabel(id='AEX0', name='Negation', begin=0, end=6)]
    assert additional_labels == expected

@pytest.mark.integration
def test_existing():
    sentence = "Unless the button is pressed."
    labels = [
        SubLabel(id='L0', name='Negation', begin=0, end=6),
        SubLabel(id='L1', name='Variable', begin=7, end=17),
        SubLabel(id='L2', name='Condition', begin=18, end=28),
        EventLabel(id='L3', name='Cause1', begin=7, end=28),
    ]

    additional_labels = label_exceptive_clauses(sentence, labels)

    assert additional_labels == []