import pytest
from dataclasses import asdict

from deepdiff import DeepDiff
from dacite import from_dict

from src.data.labels import  EventLabel, SubLabel

@pytest.mark.unit
def test_sublabel_serialization():
    label = SubLabel(id='E1', name='Variable', begin=10, end=15)
    serialized = asdict(label)
    expected = {
        'id': 'E1',
        'name': 'Variable',
        'begin': 10,
        'end': 15
    }

    differences = DeepDiff(expected, serialized)
    # the only accepted difference is the addition of a parent attribute at root level
    assert differences == {'dictionary_item_added': ["root['parent']"]}

@pytest.mark.unit
def test_sublabel_deserialization():
    data = {
        'id': 'E1',
        'name': 'Variable',
        'begin': 10,
        'end': 15
    }
    label: SubLabel = from_dict(data_class=SubLabel, data=data)

    expected = SubLabel(id='E1', name='Variable', begin=10, end=15)
    assert label == expected