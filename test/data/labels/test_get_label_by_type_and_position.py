import pytest

from src.data.labels import Label, EventLabel, SubLabel
from src.data.labels import get_label_by_type_and_position as glbtap


@pytest.mark.unit
def test_get_label_exists():
    labels = [SubLabel(id='L1', name='Variable', begin=0, end=10)]
    returned = glbtap(labels, 'Variable', 0, 10)

    assert returned == labels[0]


@pytest.mark.unit
def test_get_label_not_exists():
    labels = [SubLabel(id='L1', name='Variable', begin=0, end=10)]
    returned = glbtap(labels, 'Condition', 0, 10)

    assert returned == None


@pytest.mark.unit
def test_get_label_multiple_exist_label():
    labels = [
        SubLabel(id='L1', name='Condition', begin=0, end=10),
        SubLabel(id='L2', name='Condition', begin=0, end=10)
    ]
    returned = glbtap(labels, 'Condition', 0, 10)

    assert returned == labels[0]


@pytest.mark.unit
def test_get_label_multiple_exist_message(capsys):
    labels = [
        SubLabel(id='L1', name='Condition', begin=0, end=10),
        SubLabel(id='L2', name='Condition', begin=0, end=10)
    ]
    glbtap(labels, 'Condition', 0, 10)
    message = capsys.readouterr().out
    assert message == 'Warning: searching for a Condition label at position [0, 10] yielded multiple results.\n'
