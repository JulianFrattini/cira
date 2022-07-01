from src.data.labels import Label
from src.data.graph import Graph, EventNode

from src.converters.labelstograph.eventresolver import EventResolver

class GraphConverter:
    def __init__(self, eventresolver: EventResolver):
        self.eventresolver: EventResolver = eventresolver

    def generate_graph(self, sentence: str, labels: list[Label]) -> Graph:
        """Convert a sentence and a list of labels into a graph
        
        parameters:
            sentence -- literal sentence
            labels -- list of interconnected labels
            
        returns: a graph representing the semantic structure of the sentence and labels"""

        # generate events
        events: list[EventNode] = generate_events(labels=labels)
        for event in events:
            self.eventresolver.resolve_event(node=event, sentence=sentence)

        # rewire cause nodes with intermediate nodes representing the junctors

        # resolve negations

        # connect root-cause node with effect nodes

        return Graph(nodes=None, edges=None)

def generate_events(labels: list[Label]) -> list[EventNode]:
    """Generate an initial list of events from all event labels

    parameters:
        labels -- list of labels generated from the sentence

    returns list of event nodes, where each node is associated to the corresponding event label
    """
    events: list[EventNode] = []

    event_labels = [label for label in labels if label.name[:-1] in ['Cause', 'Effect']]
    for event_counter, event_label in enumerate(event_labels):
        events.append(EventNode(id=f'E{event_counter}', label=event_label))
    
    return events