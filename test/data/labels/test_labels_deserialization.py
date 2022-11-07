import pytest

from src.data.labels import EventLabel, SubLabel, from_dict


@pytest.mark.unit
def test_sublabel_deserialization():
    serialized = [{
        'id': 'L1',
        'name': 'Variable',
        'begin': 10,
        'end': 15,
        'parent': None
    }]
    deserialized = from_dict(serialized)

    expected = [SubLabel(id='L1', name='Variable', begin=10, end=15)]
    assert deserialized == expected


@pytest.mark.unit
def test_eventlabel_deserialization_child():
    serialized = [
        {
            'id': 'L1',
            'name': 'Variable',
            'begin': 10,
            'end': 15,
            'parent': 'L2'
        }, {
            'id': 'L2',
            'name': 'Cause1',
            'begin': 10,
            'end': 30,
            'children': ['L1'],
            'predecessor': None,
            'successor': None
        }
    ]
    deserialized = from_dict(serialized)

    l1 = SubLabel(id='L1', name='Variable', begin=10, end=15)
    l2 = EventLabel(id='L2', name='Cause1', begin=10, end=30)
    l2.add_child(l1)
    expected = [l1, l2]
    assert deserialized == expected

@pytest.mark.unit
def test_eventlabel_deserialization_children():
    serialized = [
        {
            'id': 'L1',
            'name': 'Variable',
            'begin': 10,
            'end': 15,
            'parent': 'L2'
        }, {
            'id': 'L2',
            'name': 'Cause1',
            'begin': 10,
            'end': 30,
            'children': ['L1', 'L3'],
            'predecessor': None,
            'successor': None
        }, {
            'id': 'L3',
            'name': 'Condition',
            'begin': 16,
            'end': 30,
            'parent': 'L3'
        }
    ]
    deserialized = from_dict(serialized)

    l1 = SubLabel(id='L1', name='Variable', begin=10, end=15)
    l3 = SubLabel(id='L3', name='Condition', begin=16, end=30)
    l2 = EventLabel(id='L2', name='Cause1', begin=10, end=30)
    l2.add_child(l1)
    l2.add_child(l3)
    expected = [l1, l2, l3]
    assert deserialized == expected

@pytest.mark.unit
def test_eventlabel_deserialization_successor():
    serialized = [
        {
            'id': 'L1',
            'name': 'Cause1',
            'begin': 0,
            'end': 30,
            'children': [],
            'successor': {
                'id': 'L2',
                'junctor': 'AND'
            }
        }, {
            'id': 'L2',
            'name': 'Cause2',
            'begin': 31,
            'end': 60,
            'children': [],
            'successor': None
        }
    ]
    deserialized = from_dict(serialized)

    l1 = EventLabel(id='L1', name='Cause1', begin=0, end=30)
    l2 = EventLabel(id='L2', name='Cause2', begin=31, end=60)
    l1.set_successor(l2, junctor='AND')
    expected = [l1, l2]
    assert deserialized == expected

@pytest.mark.unit
def test_eventlabel_deserialization():
    serialized = [
        {
            'id': 'L1',
            'name': 'Cause1',
            'begin': 0,
            'end': 30,
            'children': ['L1.1', 'L1.2'],
            'successor': {
                'id': 'L2',
                'junctor': 'AND'
            }
        }, {
            'id': 'L1.1',
            'name': 'Variable',
            'begin': 0,
            'end': 15,
            'parent': 'L1'
        }, {
            'id': 'L1.2',
            'name': 'Condition',
            'begin': 16,
            'end': 30,
            'parent': 'L1'
        }, {
            'id': 'L2',
            'name': 'Cause2',
            'begin': 31,
            'end': 60,
            'children': [],
            'successor': {
                'id': 'L3',
                'junctor': 'OR'
            }
        }, {
            'id': 'L3',
            'name': 'Cause3',
            'begin': 61,
            'end': 90,
            'children': [],
            'successor': None
        }, 
    ]
    deserialized = from_dict(serialized)

    l1 = EventLabel(id='L1', name='Cause1', begin=0, end=30)
    l11 = SubLabel(id='L1.1', name='Variable', begin=0, end=15)
    l12 = SubLabel(id='L1.2', name='Condition', begin=16, end=30)
    l1.add_child(l11)
    l1.add_child(l12)

    l2 = EventLabel(id='L2', name='Cause2', begin=31, end=60)
    l3 = EventLabel(id='L3', name='Cause3', begin=61, end=90)
    l1.set_successor(l2, junctor='AND')
    l2.set_successor(l3, junctor='OR')
    expected = [l1, l11, l12, l2, l3]
    assert deserialized == expected