import pytest

from src.data.graph import IntermediateNode, EventNode

@pytest.mark.integration
def test_pure_conjunction():
    c1 = EventNode(id='E1')
    c1.variable = 'var1'
    c2 = EventNode(id='E2')
    c2.variable = 'var2'
    c3 = EventNode(id='E3')
    c3.variable = 'var3'

    i1 = IntermediateNode(id='I1', conjunction=True)
    i1.add_incoming(c1)
    i1.add_incoming(c2)
    i2 = IntermediateNode(id='I2', conjunction=True)
    i2.add_incoming(c2)
    i2.add_incoming(c3)

    assert len(c2.outgoing) == 2
    c2.condense()
    assert len(c2.outgoing) == 1

    root: IntermediateNode = c3.get_root()
    assert root == i1
    assert root.conjunction == True

@pytest.mark.integration
def test_pure_disjunction():
    c1 = EventNode(id='E1')
    c1.variable = 'var1'
    c2 = EventNode(id='E2')
    c2.variable = 'var2'
    c3 = EventNode(id='E3')
    c3.variable = 'var3'

    i1 = IntermediateNode(id='I1', conjunction=False)
    i1.add_incoming(c1)
    i1.add_incoming(c2)
    i2 = IntermediateNode(id='I2', conjunction=False)
    i2.add_incoming(c2)
    i2.add_incoming(c3)

    c2.condense()

    root = c3.get_root()
    assert root == i1
    assert root.conjunction == False

@pytest.mark.integration
def test_pure_mix():
    c1 = EventNode(id='E1')
    c1.variable = 'var1'
    c2 = EventNode(id='E2')
    c2.variable = 'var2'
    c3 = EventNode(id='E3')
    c3.variable = 'var3'

    i1 = IntermediateNode(id='I1', conjunction=False)
    i1.add_incoming(c1)
    i1.add_incoming(c2)
    i2 = IntermediateNode(id='I2', conjunction=True)
    i2.add_incoming(c2)
    i2.add_incoming(c3)

    c2.condense()
    root: IntermediateNode = c2.get_root()
    assert root.conjunction == False

    child_junctor: IntermediateNode = [inc.origin for inc in root.incoming if type(inc.origin)==IntermediateNode][0]
    assert child_junctor.conjunction == True