import pytest

from src.data.graph import Node, IntermediateNode, EventNode

def test_pure_conjunction():
    c1 = EventNode(id='E1')
    c1.variable = 'var1'
    c2 = EventNode(id='E2')
    c2.variable = 'var2'
    c3 = EventNode(id='E3')
    c3.variable = 'var3'

    i1 = IntermediateNode(id='I1', conjunction=True)
    i1.add_child(c1)
    i1.add_child(c2)
    i2 = IntermediateNode(id='I2', conjunction=True)
    i2.add_child(c2)
    i2.add_child(c3)

    assert len(c2.parents) == 2
    c2.condense()
    assert len(c2.parents) == 1

    root: IntermediateNode = c3.get_root()
    assert root == i1
    assert root.conjunction == True

def test_pure_disjunction():
    c1 = EventNode(id='E1')
    c1.variable = 'var1'
    c2 = EventNode(id='E2')
    c2.variable = 'var2'
    c3 = EventNode(id='E3')
    c3.variable = 'var3'

    i1 = IntermediateNode(id='I1', conjunction=False)
    i1.add_child(c1)
    i1.add_child(c2)
    i2 = IntermediateNode(id='I2', conjunction=False)
    i2.add_child(c2)
    i2.add_child(c3)

    c2.condense()

    root = c3.get_root()
    assert root == i1
    assert root.conjunction == False


def test_pure_mix():
    c1 = EventNode(id='E1')
    c1.variable = 'var1'
    c2 = EventNode(id='E2')
    c2.variable = 'var2'
    c3 = EventNode(id='E3')
    c3.variable = 'var3'

    i1 = IntermediateNode(id='I1', conjunction=False)
    i1.add_child(c1)
    i1.add_child(c2)
    i2 = IntermediateNode(id='I2', conjunction=True)
    i2.add_child(c2)
    i2.add_child(c3)

    c2.condense()
    root: IntermediateNode = c2.get_root()
    assert root.conjunction == False

    child_junctor: IntermediateNode = [child.target for child in root.children if type(child.target)==IntermediateNode][0]
    assert child_junctor.conjunction == True