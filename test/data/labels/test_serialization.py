import pytest

from src.data.labels import  EventLabel, SubLabel

@pytest.mark.unit
def test_sublabel_serialization_parentless():
    label = SubLabel(id='L1', name='Variable', begin=10, end=15)
    serialized = label.to_dict()
    expected = {
        'id': 'L1',
        'name': 'Variable',
        'begin': 10,
        'end': 15,
        'parent': None
    }
    assert expected == serialized

@pytest.mark.unit
def test_sublabel_serialization_parent():
    label = SubLabel(id='L1', name='Variable', begin=10, end=15)
    parent = EventLabel(id='L2', name='Cause1', begin=10, end=30)
    parent.add_child(child=label)
    serialized = label.to_dict()

    expected = {
        'id': 'L1',
        'name': 'Variable',
        'begin': 10,
        'end': 15,
        'parent': 'L2'
    }
    assert expected == serialized

@pytest.mark.unit
def test_evetlabel_serialization_child():
    cause1 = EventLabel(id='L1', name='Cause1', begin=0, end=30)
    variable = SubLabel(id='L2', name='Variable', begin=0, end=10)
    cause1.add_child(variable)
    serialized = cause1.to_dict()

    expected = {
        'id': 'L1',
        'name': 'Cause1',
        'begin': 0,
        'end': 30,
        'predecessor': None,
        'successor': None,
        'children': ['L2']
    }
    assert expected == serialized

@pytest.mark.unit
def test_evetlabel_serialization_children():
    cause1 = EventLabel(id='L1', name='Cause1', begin=0, end=30)
    variable = SubLabel(id='L2', name='Variable', begin=0, end=10)
    condition = SubLabel(id='L3', name='Condition', begin=11, end=30)
    cause1.add_child(variable)
    cause1.add_child(condition)
    serialized = cause1.to_dict()

    expected = {
        'id': 'L1',
        'name': 'Cause1',
        'begin': 0,
        'end': 30,
        'predecessor': None,
        'successor': None,
        'children': ['L2', 'L3']
    }
    assert expected == serialized

@pytest.mark.unit
def test_evetlabel_serialization_successor():
    cause1 = EventLabel(id='L1', name='Cause1', begin=0, end=30)
    cause2 = EventLabel(id='L2', name='Cause2', begin=31, end=60)
    cause1.set_successor(cause2, junctor='AND')
    serialized = cause1.to_dict()

    expected = {
        'id': 'L1',
        'name': 'Cause1',
        'begin': 0,
        'end': 30,
        'predecessor': None,
        'successor': {
            'id': 'L2',
            'junctor': 'AND'
        },
        'children': []
    }
    assert expected == serialized

@pytest.mark.unit
def test_evetlabel_serialization_predecessor():
    cause1 = EventLabel(id='L1', name='Cause1', begin=0, end=30)
    cause2 = EventLabel(id='L2', name='Cause2', begin=31, end=60)
    cause1.set_successor(cause2, junctor='OR')
    serialized = cause2.to_dict()

    expected = {
        'id': 'L2',
        'name': 'Cause2',
        'begin': 31,
        'end': 60,
        'predecessor': {
            'id': 'L1',
            'junctor': 'OR'
        },
        'successor': None,
        'children': []
    }
    assert expected == serialized

@pytest.mark.unit
def test_evetlabel_serialization_successor_predecessor():
    cause1 = EventLabel(id='L1', name='Cause1', begin=0, end=30)
    cause2 = EventLabel(id='L2', name='Cause2', begin=31, end=60)
    cause3 = EventLabel(id='L3', name='Cause3', begin=61, end=90)
    cause1.set_successor(cause2, junctor='AND')
    cause2.set_successor(cause3, junctor='OR')
    serialized = cause2.to_dict()

    expected = {
        'id': 'L2',
        'name': 'Cause2',
        'begin': 31,
        'end': 60,
        'predecessor': {
            'id': 'L1',
            'junctor': 'AND'
        },
        'successor': {
            'id': 'L3',
            'junctor': 'OR'
        },
        'children': []
    }
    assert expected == serialized

@pytest.mark.unit
def test_evetlabel_serialization_successor_predecessor_children():
    cause2 = EventLabel(id='L2', name='Cause2', begin=31, end=60)
    
    variable = SubLabel(id='L4', name='Variable', begin=0, end=10)
    condition = SubLabel(id='L5', name='Condition', begin=11, end=30)
    cause2.add_child(variable)
    cause2.add_child(condition)

    cause1 = EventLabel(id='L1', name='Cause1', begin=0, end=30)
    cause3 = EventLabel(id='L3', name='Cause3', begin=61, end=90)
    cause1.set_successor(cause2, junctor='AND')
    cause2.set_successor(cause3, junctor='OR')
    serialized = cause2.to_dict()

    expected = {
        'id': 'L2',
        'name': 'Cause2',
        'begin': 31,
        'end': 60,
        'predecessor': {
            'id': 'L1',
            'junctor': 'AND'
        },
        'successor': {
            'id': 'L3',
            'junctor': 'OR'
        },
        'children': ['L4', 'L5']
    }
    assert expected == serialized