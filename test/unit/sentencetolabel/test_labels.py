import pytest

from src.data.labels import  EventLabel, SubLabel

@pytest.mark.unit
def test_create_eventlabel_emptychildren():
    el = EventLabel(id='T1', name='Cause1', begin=1, end=5)

    assert len(el.children) == 0

@pytest.mark.unit
def test_create_eventlabel_addchild():
    el = EventLabel(id='T1', name='Cause1', begin=1, end=5)
    l = SubLabel(id='T2', name='Condition', begin=1, end=3)
    
    el.add_child(l)
    assert len(el.children) == 1

@pytest.mark.unit
def test_create_eventlabel_addchild():
    el = EventLabel(id='T1', name='Cause1', begin=1, end=5)
    l = SubLabel(id='T2', name='Condition', begin=1, end=3)
    
    el.add_child(l)
    assert l.parent == el

@pytest.mark.unit
def test_create_sublabel():
    l = SubLabel(id='T2', name='Condition', begin=1, end=3)

    assert l.parent == None