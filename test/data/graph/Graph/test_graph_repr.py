import pytest

from src.data.graph import Graph, IntermediateNode, EventNode, Edge

@pytest.mark.integration
def test_graph_representation():
    root = IntermediateNode(id='i1', conjunction=True)
    cause1 = EventNode(id='c1', variable='an error', condition='occurs')
    cause2 = EventNode(id='c2', variable='the admin', condition='is notified')
    root.add_incoming(cause1)
    root.add_incoming(cause2, negated=True)

    effect = EventNode(id='e1', variable='the admin', condition='receives a push notification')
    effect.add_incoming(root)

    graph = Graph(nodes = [cause1, cause2, root, effect], root=root, edges=None)

    assert graph.__repr__() == f'([{cause1.variable}].({cause1.condition}) && NOT [{cause2.variable}].({cause2.condition})) ===> [{effect.variable}].({effect.condition})'