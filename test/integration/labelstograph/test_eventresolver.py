import pytest

from src.converters.labelstograph.eventresolver import SimpleResolver

from src.data.graph import EventNode
from src.data.labels import EventLabel, SubLabel

@pytest.mark.integration
def test_simple():
    resolver = SimpleResolver()
    sentence = "When the red button is pushed the system shuts down."

    c1 = EventLabel(id='L1', name='Cause1', begin=5, end=29)
    c1_v = SubLabel(id='L2', name='Variable', begin=5, end=19)
    c1_c = SubLabel(id='L3', name='Condition', begin=20, end=29)
    c1.add_child(c1_c)
    c1.add_child(c1_v)

    event1 = EventNode(id='N1', label=c1)
    resolver.resolve_event(node=event1, sentence=sentence)

    assert event1.variable == "the red button"
    assert event1.condition == "is pushed"

@pytest.mark.integration
def test_split():
    resolver = SimpleResolver()
    sentence = "When the red is button pushed the system shuts down."

    c1 = EventLabel(id='L1', name='Cause1', begin=5, end=29)
    c1_v1 = SubLabel(id='L2', name='Variable', begin=5, end=12)
    c1_c1 = SubLabel(id='L3', name='Condition', begin=13, end=15)
    c1_v2 = SubLabel(id='L4', name='Variable', begin=16, end=22)
    c1_c2 = SubLabel(id='L5', name='Condition', begin=23, end=29)
    c1.add_child(c1_c1)
    c1.add_child(c1_v1)
    c1.add_child(c1_c2)
    c1.add_child(c1_v2)

    event1 = EventNode(id='N1', label=c1)
    resolver.resolve_event(node=event1, sentence=sentence)

    assert event1.variable == "the red button"
    assert event1.condition == "is pushed"

@pytest.mark.integration
def test_move1_variable():
    resolver = SimpleResolver()
    sentence = "If the button is pressed or released"

    c1 = EventLabel(id='L1', name='Cause1', begin=3, end=24)
    c1.add_child(SubLabel(id='L2', name='Variable', begin=3, end=13))
    c1.add_child(SubLabel(id='L3', name='Condition', begin=14, end=24))
    c2 = EventLabel(id='L4', name='Cause1', begin=28, end=36)
    c2.add_child(SubLabel(id='L5', name='Condition', begin=28, end=36))

    c1.set_successor(c2)

    event2 = EventNode(id='N1', label=c2)
    resolver.resolve_event(node=event2, sentence=sentence)

    assert event2.variable == "the button"

@pytest.mark.integration
def test_move1_condition():
    resolver = SimpleResolver()
    sentence = "If the button or the link is pressed"

    c1 = EventLabel(id='L1', name='Cause1', begin=3, end=13)
    c1.add_child(SubLabel(id='L2', name='Variable', begin=3, end=13))
    c2 = EventLabel(id='L4', name='Cause1', begin=17, end=36)
    c1.add_child(SubLabel(id='L2', name='Variable', begin=17, end=25))
    c2.add_child(SubLabel(id='L5', name='Condition', begin=26, end=36))

    c1.set_successor(c2)

    event1 = EventNode(id='N1', label=c1)
    resolver.resolve_event(node=event1, sentence=sentence)

    assert event1.condition == "is pressed"