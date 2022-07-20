from typing import Tuple
import pytest

from src.data.graph import Node, Edge

@pytest.fixture
def tree() -> Tuple[Node, Node]:
    # generate two generic nodes
    root = Node(id='r')
    leaf = Node(id='l')

    # connect the root and the leaf with an edge
    edge = Edge(origin=leaf, target=root, negated=False)
    root.incoming.append(edge)
    leaf.outgoing.append(edge)

    return leaf, root

@pytest.mark.unit
def test_get_root_of_leaf(tree):
    leaf, root = tree

    assert leaf.get_root() == root

@pytest.mark.unit
def test_get_root_of_root(tree):
    _, root = tree

    assert root.get_root() == root