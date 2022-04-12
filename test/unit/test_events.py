import pytest

from src.converter2.util.event import Event
from src.converter2.util.labels import Label, EventLabel

@pytest.mark.unit
def test_getVariable_single():
    var1 = Label(id='1', name='Variable', begin=0, end=9, sentence='a fireman')
    cause = EventLabel(id='2', name='Cause1', begin=0, end=9, children=[var1])

    event = Event(name='Cause1', labels=[cause])
    assert event.getVariable() == 'a fireman'

@pytest.mark.unit
def test_getVariable_multi():
    var1 = Label(id='1', name='Variable', begin=0, end=9, sentence='a fireman')
    var2 = Label(id='2', name='Variable', begin=0, end=5, sentence='truck')
    cause = EventLabel(id='3', name='Cause1', begin=0, end=14, children=[var1, var2])

    event = Event(name='Cause1', labels=[cause])
    assert event.getVariable() == 'a fireman truck'


@pytest.mark.unit
def test_getVariable_predecessor():
    var1 = Label(id='1', name='Variable', begin=0, end=9, sentence='a fireman')
    cause1 = EventLabel(id='2', name='Cause1', begin=0, end=14, children=[var1])
    event1 = Event(name='Cause1', labels=[cause1])

    cause2 = EventLabel(id='3', name='Cause2', begin=0, end=14, children=[])
    event2 = Event(name='Cause2', labels=[cause2])

    event1.setSuccessor(event2)
    event2.setPredecessor(event1)

    assert event2.getVariable() == 'a fireman'

@pytest.mark.unit
def test_getVariable_predecessor2():
    var1 = Label(id='1', name='Variable', begin=0, end=9, sentence='a fireman')
    cause1 = EventLabel(id='2', name='Cause1', begin=0, end=14, children=[var1])
    event1 = Event(name='Cause1', labels=[cause1])

    cause2 = EventLabel(id='3', name='Cause2', begin=0, end=14, children=[])
    event2 = Event(name='Cause2', labels=[cause2])
    
    cause3 = EventLabel(id='4', name='Cause3', begin=0, end=14, children=[])
    event3 = Event(name='Cause2', labels=[cause2])

    event1.setSuccessor(event2)
    event2.setPredecessor(event1)

    event2.setSuccessor(event3)
    event3.setPredecessor(event2)

    assert event3.getVariable() == 'a fireman'