from src.data.labels import Label
from src.data.graph import Graph, Node, EventNode, IntermediateNode, Edge

def connect_events(events: list[EventNode]) -> list[Node]:
    """Connect a list of events based on the relationships between them to a tree, where the root nodes represent events and all intermediate nodes represent junctors"""
    nodes: list[Node] = []

    if len(events) == 1:
        # in case there is only one event node, there are no junctors to resolve and events to connect
        nodes.append(events[0])
    else:
        # in case there are at least two event nodes, resolve the junctors by introducing intermediate nodes
        junctor_map: dict = get_junctors(events=events)


    return nodes

def get_junctors(events: list[EventNode]) -> dict:
    """Obtain a map that maps two adjacent event nodes to their respective junctor (conjunction or disjunction). If no explicit junctor is given, take the junctor between the (recursively) next pair of event nodes
    
    parameters:
        events -- list of event nodes
        
    returns: map from pairs of event node ids to a junctor (AND/OR)"""
    
    junctor_map = {}

    # get the starting node (the cause event node which has no predecessor)
    current_node: EventNode = [event for event in events if (event.label.predecessor == None)][0]
    while current_node.label.successor != None:
        junctor_map[(current_node.label.id, current_node.label.successor.target.id)] = current_node.label.successor.junctor
        current_node = [event for event in events if event.label==current_node.label.successor.target][0]

    # fill all implicit junctors
    previous = 'AND'
    for nodepair in list(junctor_map.keys())[::-1]:
        if junctor_map[nodepair] == None:
            junctor_map[nodepair] = previous
        else:
            previous = junctor_map[nodepair]

    return junctor_map

def generate_initial_nodenet(events: list[Node], junctor_map: dict) -> list[IntermediateNode]:
    junctors: list[IntermediateNode] = []

    for index, junctor in enumerate(junctor_map):
        intermediate = IntermediateNode(id=f'I{index}', conjunction=(junctor_map[junctor]=='AND'))
        joined_nodes = [event for event in events if (event.id in junctor)]
        intermediate.add_children(joined_nodes)
        junctors.append(intermediate)

    return junctors