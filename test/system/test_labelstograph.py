import pytest

from src.cira import l2g
from src.converter2.util.graph import EventNode, IntermediateNode, Graph

#@pytest.mark.system
def test_sentence():
    text = "If a fire breaks out in the building and either no firemen are around or the people start to panic, the building needs to be evacuated."

    labels = [{"id": "T1", "label": "Variable", "begin": 3, "end": 9}, {"id": "T2", "label": "Cause1", "begin": 3, "end": 36}, {"id": "T3", "label": "Condition", "begin": 10, "end": 36}, {"id": "T4", "label": "Conjunction", "begin": 37, "end": 40}, {"id": "T5", "label": "Negation", "begin": 48, "end": 50}, {"id": "T6", "label": "Variable", "begin": 51, "end": 58}, {"id": "T7", "label": "Cause2", "begin": 48, "end": 69}, {"id": "T8", "label": "Condition", "begin": 59, "end": 69}, {"id": "T9", "label": "Disjunction", "begin": 70, "end": 72}, {"id": "T10", "label": "Variable", "begin": 73, "end": 83}, {"id": "T11", "label": "Cause3", "begin": 73, "end": 98}, {"id": "T12", "label": "Condition", "begin": 84, "end": 98}, {"id": "T13", "label": "Variable", "begin": 100, "end": 112}, {"id": "T14", "label": "Effect1", "begin": 100, "end": 134}, {"id": "T15", "label": "Condition", "begin": 113, "end": 134}]
 
    
    graph = l2g(text, labels)

    c1 = EventNode(cause=True, variable='a fire')
    c2 = EventNode(cause=True, variable='firemen')
    i1 = IntermediateNode(conjunction=True, children=[c1, c2])

    c3 = EventNode(cause=True, variable='the people')
    i2 = IntermediateNode(conjunction=False, children=[i1, c3])

    e = EventNode(cause=False, variable='Effect1')
    expected = Graph(rootcause=i2, effects=[e])

    assert graph == expected