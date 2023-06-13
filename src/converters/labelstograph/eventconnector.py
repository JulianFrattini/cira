from typing import Tuple
from src.data.graph import  Node, EventNode, IntermediateNode, Edge

def connect_events(events: list[EventNode]) -> Tuple[list[Node], list[Edge]]:
    """Connect a list of events based on the relationships between them to a tree, where the leaf nodes represent events and all intermediate nodes represent junctors
    
    parameters:
        events -- list of events to connect (applicable for neighboring events connected with junctors)

    returns: minimal list of nodes representing a tree (with the root node at position 0)
    """
    if len(events) == 1:
        # in case there is only one event node, there are no junctors to resolve and events to connect
        return (events, [])
    else:
        # in case there are at least two event nodes, resolve the junctors by introducing intermediate nodes
        junctor_map: dict = get_junctors(events=events)
        _, edges = generate_initial_nodenet(events=events, junctor_map=junctor_map)
        edgelist: list[Edge] = edges

        # ensure that every leaf node has exactly one parent
        all_removable_edges: list[Edge] = []
        all_new_edges: list[Edge] = []
        for event in events:
            removable_edges, new_edges = event.condense()
            all_removable_edges = all_removable_edges + removable_edges
            all_new_edges = all_new_edges + new_edges
        # remove the deleted edges from the edgelist
        for edge in all_removable_edges:
            edgelist.remove(edge)
        # add the new edges to the edgelist
        edgelist = edgelist + all_new_edges
        
        # obtain the root node:
        root = events[0].get_root()
        return (root.flatten(), edgelist)

def get_junctors(events: list[EventNode]) -> dict:
    """Obtain a dictionary that maps two adjacent event nodes to their respective junctor (conjunction or disjunction). If no explicit junctor is given, (recursively) take the junctor between the next pair of event nodes
    
    parameters:
        events -- list of event nodes
        
    returns: map from pairs of event node ids to a junctor (AND/OR)"""
    
    junctor_map = {}

    # get the starting node (the cause event node associated to the event label with the lowest begin index)
    current_node: EventNode = sorted(events, key=lambda event: event.labels[0].begin, reverse=False)[0]
    while current_node.labels[-1].successor != None:
        label1 = current_node.labels[-1]
        label2 = label1.successor.target
        # only consider junctors between labels of the same type (Cause or effect)
        if label1.is_cause() == label2.is_cause():
            # obtain the node with which the current node is joined and denote the junctor
            next_node = [event for event in events if label2 in event.labels][0]
            junctor_map[(current_node.id, next_node.id)] = label1.successor.junctor
            # continue with that node
            current_node = next_node
        else:
            break

    # fill all implicit junctors by traversing the junctor map in reverse order (as explicit junctors tend to appear towards the and, like in "If a [?], b [?], c [?], [AND] d, then e.")
    previous = 'AND'
    for nodepair in list(junctor_map.keys())[::-1]:
        if junctor_map[nodepair] == None:
            junctor_map[nodepair] = previous
        else:
            previous = junctor_map[nodepair]

    return junctor_map

def generate_initial_nodenet(events: list[Node], junctor_map: dict) -> Tuple[list[IntermediateNode], list[Edge]]:
    """Generates the intermediate nodes that initially connect the list of events. The type of intermediate node (conjunction/disjunction) is derived from the junctor map.
    
    parameters: 
        events -- list of events to connect
        junctor_map -- dict which connects every two adjacent events with a junctor ('AND'/'OR')
        
    returns: a list of intermediate nodes connecting the event nodes"""
    junctors: list[IntermediateNode] = []
    edgelist: list[Edge] = []

    for index, junctor in enumerate(junctor_map):
        intermediate = IntermediateNode(
            id=f'I{index}', 
            conjunction=(junctor_map[junctor]=='AND'),
            precedence=(junctor_map[junctor].startswith('P')))
        joined_nodes: list[EventNode] = [event for event in events if (event.id in junctor)]
        for node in joined_nodes:
            is_negated: bool = (bool) (node.is_negated())
            edge = intermediate.add_incoming(child=node, negated=is_negated)
            edgelist.append(edge)
        junctors.append(intermediate)

    return (junctors,edgelist)