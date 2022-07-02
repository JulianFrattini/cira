from abc import ABC, abstractmethod

from src.data.graph import EventNode
from src.data.labels import EventLabel

class EventResolver(ABC):
    @abstractmethod
    def resolve_event(self, node: EventNode, sentence: str):
        pass

class SimpleResolver(EventResolver):
    def resolve_event(self, node: EventNode, sentence: str):
        """Determine the variable and the condition of a node dependent on the following conditions: (1) if the EventLabel associated to the EventNode has at least one SubLabel child that is a variable/condition, use the text covered by those labels as variable/condition."""

        for attribute in ['Variable', 'Condition']:
            candidates = [node.label] + get_events_in_order(label=node.label, attribute=attribute)

            for candidate in candidates:
                value = candidate.get_attribute(attribute=attribute, sentence=sentence)
                if value != None:
                    setattr(node, attribute.lower(), value)
                    break

def get_events_in_order(label: EventLabel, attribute: str) -> list[EventLabel]:
    """Obtain a list of EventLabel's in the order of relevance (dominant order for variables is preceeding, because in case of a missing variable (e.g., "the red button is pressed or released") the variable is more likely to be located in the preceeding event, and for conditions is succeeding), preferring events of the same type (cause/effect).

    parameters:
        label -- label to start constructing the order from
        attribute -- either 'Variable' or 'Condition'

    returns: list of neighboring event labels in order of relevance
    """
    candidates: list[EventLabel] = []

    for etype in (['Cause', 'Effect'] if label.name[:-1]=='Cause' else ['Effect', 'Cause']):
        for direction in (['predecessor', 'successor'] if attribute=='Variable' else ['successor', 'predecessor']):
            candidates = candidates + get_all_neighbors_of_type(startlabel=label, direction=direction, type=etype)

    return candidates

def get_all_neighbors_of_type(startlabel: EventLabel, direction: str, type: str) -> list[EventLabel]:
    """Starting from a given label and going into a specific direction, add all labels of the same type to a list

    parameters:
        startlabel -- the label to start searching from (will not be added to the list)
        direction -- either 'predecessor' or 'successor', depending on the direction to search in
        type -- either 'Cause' or 'Effect'

    returns: list of all labels of the given type that are located in the given direction of the start label
    """
    result: list[EventLabel] = []

    next_label = startlabel
    while getattr(next_label, direction) != None:
        neighbor = getattr(next_label, direction)
        next_label: EventLabel = getattr(neighbor, 'target' if direction=='successor' else 'origin')
        if next_label.name.startswith(type):
            result.append(next_label)

    return result