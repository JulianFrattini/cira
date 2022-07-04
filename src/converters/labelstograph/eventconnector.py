from src.data.graph import  Node, EventNode, IntermediateNode

def connect_events(events: list[EventNode]) -> list[Node]:
    """Connect a list of events based on the relationships between them to a tree, where the leaf nodes represent events and all intermediate nodes represent junctors
    
    parameters:
        events -- list of events to connect (applicable for neighboring events connected with junctors)

    returns: minimal list of nodes representing a tree (with the root node at position 0)
    """
    nodes: list[Node] = []

    if len(events) == 1:
        # in case there is only one event node, there are no junctors to resolve and events to connect
        nodes.append(events[0])
    else:
        # in case there are at least two event nodes, resolve the junctors by introducing intermediate nodes
        junctor_map: dict = get_junctors(events=events)
        nodenet = generate_initial_nodenet(events=events, junctor_map=junctor_map)

        # ensure that every leaf node has exactly one parent
        for event in events:
            event.condense()
        
        # obtain the root node:
        root = events[0].get_root()
        nodes = root.flatten()
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
        label1 = current_node.label
        label2 = current_node.label.successor.target
        if label1.is_cause() == label2.is_cause():
            # only determine junctors between labels of the same type
            # TODO: currently, the junctor map uses the ids of the labels, not the events, as an identifier
            #junctor_map[(current_node.id, current_node.label.successor.target.id)] = current_node.label.successor.junctor
            junctor_map[(current_node.label.id, current_node.label.successor.target.id)] = current_node.label.successor.junctor
            current_node = [event for event in events if event.label==current_node.label.successor.target][0]
        else:
            # if the the events do not contain the successor, then because the successor is outside ouf the events list
            # for example: a cause label neighboring an effect label is not supposed to produce a junctor mapping
            break

    # fill all implicit junctors
    previous = 'AND'
    for nodepair in list(junctor_map.keys())[::-1]:
        if junctor_map[nodepair] == None:
            junctor_map[nodepair] = previous
        else:
            previous = junctor_map[nodepair]

    return junctor_map

def generate_initial_nodenet(events: list[Node], junctor_map: dict) -> list[IntermediateNode]:
    """Generates the intermediate nodes that initially connect the list of events. The type of intermediate node (conjunction/disjunction) is derived from the junctor map.
    
    parameters: 
        events -- list of events to connect
        junctor_map -- dict which connects every two adjacent events with a junctor ('AND'/'OR')
        
    returns: a list of intermediate nodes connecting the event nodes"""
    junctors: list[IntermediateNode] = []

    for index, junctor in enumerate(junctor_map):
        intermediate = IntermediateNode(id=f'I{index}', conjunction=(junctor_map[junctor]=='AND'))
        joined_nodes: list[EventNode] = [event for event in events if (event.label.id in junctor)]
        for node in joined_nodes:
            is_negated: bool = (bool) (node.is_negated())
            intermediate.add_child(child=node, negated=is_negated)
        junctors.append(intermediate)

    return junctors