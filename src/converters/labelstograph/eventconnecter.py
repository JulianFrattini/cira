from src.data.labels import Label
from src.data.graph import Graph, Node, EventNode, IntermediateNode, Edge

def connect_events(events: list[EventNode], labels: list[Label]) -> list[Node]:

    junctor_map: dict = get_junctors(events=events, labels=labels)

    return None

def get_junctors(events: list[EventNode]) -> dict:
    """Obtain a map that maps two adjacent event nodes to their respective junctor (conjunction or disjunction). If no explicit junctor is given, take the junctor between the (recursively) next pair of event nodes
    
    parameters:
        events -- list of event nodes
        
    returns: map from pairs of event node ids to a junctor (AND/OR)"""
    
    junctor_map = {}

    # get the starting node (the cause event node which has no predecessor)
    current_node: EventNode = [event for event in events if (event.is_cause() and event.label.predecessor == None)][0]
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