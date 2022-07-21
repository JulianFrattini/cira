import pytest 

from src.data.graph import Graph, Node

@pytest.mark.unit
def test_existing():
    nodes = [Node(id=f'n{i}') for i in range(5)]
    graph = Graph(nodes=nodes, root=None, edges=None)

    assert graph.get_node(id='n0') == nodes[0]

@pytest.mark.unit
def test_nonexisting_returns_none():
    nodes = [Node(id=f'n{i}') for i in range(5)]
    graph = Graph(nodes=nodes, root=None, edges=None)

    assert graph.get_node(id='n10') == None

@pytest.mark.unit
def test_nonexisting_output(capsys):
    nodes = [Node(id=f'n{i}') for i in range(5)]
    graph = Graph(nodes=nodes, root=None, edges=None)

    graph.get_node(id='n10')
    captured = capsys.readouterr()
    assert f'No node with id n10 found in {nodes}' in captured.out