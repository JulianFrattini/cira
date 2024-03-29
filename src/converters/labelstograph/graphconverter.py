import src.util.constants as consts
from src.converters.labelstograph.eventconnector import connect_events
from src.converters.labelstograph.eventresolver import EventResolver
from src.data.graph import EventNode, Graph, Node
from src.data.labels import EventLabel, Label


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
        negated_event_labels: list[EventLabel] = resolve_exceptive_negations(labels)
        for event_label in negated_event_labels:
            event = [e for e in events if (event_label in e.labels)][0]
            event.exceptive_negation = True

        # connect cause nodes with intermediate nodes representing the junctors
        cause_nodes = [event for event in events if event.is_cause()]
        causes, edgelist = connect_events(events=cause_nodes)
        cause_root: Node = causes[0]

        # connect root-cause node to effect nodes
        effects = [event for event in events if not event.is_cause()]
        for effect in effects:
            # check for double-negation
            is_double_negative = (len(causes) == 1) and (causes[0].is_negated())
            is_negated=effect.is_negated() != is_double_negative
            edge = effect.add_incoming(child=cause_root, negated=is_negated)
            edgelist.append(edge)

        return Graph(nodes=causes+effects, root=cause_root, edges=edgelist)

def generate_events(labels: list[Label]) -> list[EventNode]:
    """Generate an initial list of events from all event labels

    parameters:
        labels -- list of labels generated from the sentence

    returns list of event nodes, where each node is associated to the corresponding event label
    """
    events: list[EventNode] = []

    only_event_labels_not_unique = [label.name for label in labels if consts.is_event(label.name[:-1])]
    # obtain the unique event label names (e.g., Cause1, Effect2)
    unique_event_labels_names: list[str] = []
    for label_name in only_event_labels_not_unique:
        if label_name not in unique_event_labels_names:
            unique_event_labels_names.append(label_name)

    for event_counter, event_label_name in enumerate(unique_event_labels_names):
        event_labels = [label for label in labels if label.name==event_label_name]
        events.append(EventNode(id=f'E{event_counter}', labels=event_labels))
    return events

def resolve_exceptive_negations(labels: list[Label]) -> list[EventLabel]:
    """Negated events are handled internally by each node resulting from an event label, but exceptive negations ("Unless A then B") have to be handled manually. This method identifies exceptive negations and identifies all events (in the form of event labels) that are affected by the additional negation.

    parameters:
        labels -- list of labels generated from the sentence

    returns: list of labels that are affected by an exceptive negation and hence need to be additionally negated"""
    exceptive_negations = [label for label in labels if label.name==consts.NEGATION and label.parent is None]

    all_events: list[EventLabel] = [label for label in labels if type(label)==EventLabel]
    all_events.sort(key=(lambda event: event.begin))

    # determine all additionally negated events, i.e., the event immediately following the exceptive negation plus all additional events that are connected to that event through conjunctions
    negated_events: list[EventLabel] = []
    for negation in exceptive_negations:
        affected_event = [label for label in all_events if label.begin > negation.end][0]
        negated_events.append(affected_event)
        while affected_event.successor is not None and affected_event.successor.junctor == consts.AND:
            affected_event = affected_event.successor.target
            negated_events.append(affected_event)

    return negated_events
