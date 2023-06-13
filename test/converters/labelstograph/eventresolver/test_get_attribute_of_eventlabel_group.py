import pytest

from src.converters.labelstograph.eventresolver import get_attribute_of_eventlabel_group

from src.data.labels import EventLabel, SubLabel

@pytest.mark.integration
def test_single_label():
    sentence: str = "When the red button is pushed the system shuts down."

    c1 = EventLabel(id='L1', name='Cause1', begin=5, end=29)
    c1.add_child(SubLabel(id='L2', name='Variable', begin=5, end=19))
    event_group = [c1]

    result = get_attribute_of_eventlabel_group(event_group, attribute="Variable", sentence=sentence)

    assert result == 'the red button'

@pytest.mark.integration
def test_spread_event_label():
    sentence: str = "Users which are older than 18 years, are allowed to drive."

    c1_1 = EventLabel(id='L1', name='Cause1', begin=0, end=5)
    c1_1.add_child(SubLabel(id='L2', name='Variable', begin=0, end=5))
    c1_2 = EventLabel(id='L3', name='Cause1', begin=12, end=35)
    c1_2.add_child(SubLabel(id='L4', name='Condition', begin=12, end=35))

    c1_1.set_successor(c1_2, junctor='MERGE')
    event_group = [c1_1, c1_2]

    variable = get_attribute_of_eventlabel_group(event_group, attribute='Variable', sentence=sentence)
    condition = get_attribute_of_eventlabel_group(event_group, attribute='Condition', sentence=sentence)

    assert variable == 'Users'
    assert condition == 'are older than 18 years'

@pytest.mark.integration
def test_spread_sublabel():
    sentence: str = "Data transmission is only possible if the user consented to it."

    c1_1 = EventLabel(id='L1', name='Effect1', begin=0, end=20)
    c1_1.add_child(SubLabel(id='L2', name='Variable', begin=0, end=17))
    c1_1.add_child(SubLabel(id='L3', name='Condition', begin=18, end=20))
    c1_2 = EventLabel(id='L4', name='Effect1', begin=26, end=34)
    c1_2.add_child(SubLabel(id='L5', name='Condition', begin=26, end=34))

    c1_1.set_successor(c1_2, junctor='MERGE')
    event_group = [c1_1, c1_2]

    variable = get_attribute_of_eventlabel_group(event_group, attribute='Variable', sentence=sentence)
    condition = get_attribute_of_eventlabel_group(event_group, attribute='Condition', sentence=sentence)

    assert variable == 'Data transmission'
    assert condition == 'is possible'
