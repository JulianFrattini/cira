import pytest

from src.data.graph import IntermediateNode

@pytest.mark.unit
def test_disjunction():
    node: IntermediateNode = IntermediateNode(id='i', conjunction=False, precedence=False)
    assert node.get_precedence_value() == 1

@pytest.mark.unit
def test_conjunction():
    node: IntermediateNode = IntermediateNode(id='i', conjunction=True, precedence=False)
    assert node.get_precedence_value() == 2

@pytest.mark.unit
def test_disjunction_overruled_precedence():
    node: IntermediateNode = IntermediateNode(id='i', conjunction=False, precedence=True)
    assert node.get_precedence_value() == 3