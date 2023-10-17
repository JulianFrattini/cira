from abc import ABC, abstractmethod

from src.data.graph import EventNode
from src.data.labels import EventLabel

import src.util.constants as consts

class EventResolver(ABC):
    @abstractmethod
    def resolve_event(self, node: EventNode, sentence: str):
        pass


class SimpleResolver(EventResolver):
    def resolve_event(self, node: EventNode, sentence: str):
        """Determine the variable and the condition of a node dependent on the following conditions: (1) if the EventLabel associated to the EventNode has at least one SubLabel child that is a variable/condition, use the text covered by those labels as variable/condition.

        parameters:
            node -- the node where the variable and condition shall be set
            sentence -- the verbatim sentence from which the variable and condition will be taken"""

        for attribute in [consts.VARIABLE, consts.CONDITION]:
            candidates: list[EventLabel] = node.labels + \
                get_events_in_order(starting_node=node, attribute=attribute)
            candidates_grouped: list[list[EventLabel]
                                     ] = join_event_labels(candidates)

            for candidate_group in candidates_grouped:
                node_attribute: str = get_attribute_of_eventlabel_group(
                    event_label_group=candidate_group, attribute=attribute, sentence=sentence)

                if node_attribute != None:
                    setattr(node, attribute.lower(), node_attribute)
                    break


def get_events_in_order(starting_node: EventNode, attribute: str) -> list[EventLabel]:
    """Obtain a list of EventLabel's in the order of relevance (dominant order for variables is preceeding, because in case of a missing variable (e.g., "the red button is pressed or released") the variable is more likely to be located in the preceeding event, and for conditions is succeeding), preferring events of the same type (cause/effect).

    parameters:
        label -- label to start constructing the order from
        attribute -- either 'Variable' or 'Condition'

    returns: list of neighboring event labels in order of relevance
    """
    candidates: list[EventLabel] = []

    is_cause = event_is_type_cause(starting_node)
    events_ordered = [consts.CAUSE, consts.EFFECT] if is_cause else [consts.EFFECT, consts.CAUSE]

    for event_type in events_ordered:
        is_variable = attribute == consts.VARIABLE
        directions_ordered = [consts.PREDECESSOR, consts.SUCCESSOR] if is_variable else [consts.SUCCESSOR, consts.PREDECESSOR]
        for direction in directions_ordered:
            # determine the label to start with
            label_idx = 0 if direction == consts.PREDECESSOR else -1
            starting_label = starting_node.labels[label_idx]
            candidates = candidates + \
                get_all_neighbors_of_type(
                    startlabel=starting_label, direction=direction, type=event_type)

    return candidates


def event_is_type_cause(node: EventNode) -> bool:
    """Determine wheter an event is from type 'Cause'

    parameters: event -- the EventNode

    return: true if event is 'Cause'
    """
    return node.labels[0].name[:-1] == consts.CAUSE


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

        next_direction = consts.TARGET if direction == consts.SUCCESSOR else consts.ORIGIN
        next_label: EventLabel = getattr( neighbor, next_direction)

        if next_label.name.startswith(type):
            result.append(next_label)

    return result


def join_event_labels(event_labels: list[EventLabel]) -> list[list[EventLabel]]:
    """Given a list of event labels, return a list of list of labels, where every sub-list contains all adjacent labels of the same type (e.g., Cause1).

    parameters:
        event_labels -- list of EventLabels in order of relevance

    returns: list of lists, where each sublist contains all adjacent event labels of the same type"""

    joined_list: list[list[EventLabel]] = []

    current_type: str = ""
    type_list: list[EventLabel] = []
    for event_label in event_labels:
        if event_label.name != current_type:
            if len(type_list) > 0:
                joined_list.append(type_list)

            # reset the list containing all labels of the current type
            type_list = []

            # remember the current type
            current_type = event_label.name

        type_list.append(event_label)

    # add the final list of labels from the last observed type
    joined_list.append(type_list)

    return joined_list


def get_attribute_of_eventlabel_group(event_label_group: list[EventLabel], attribute: str, sentence: str) -> str:
    """Given a list of event labels of the same type (e.g., Cause1), determine the attribute (either "Variable" or "Condition") of this event by (1) determining all relevant sublabels (as the list of event labels might be associated with multiple sublabels for that attribute) and (2) extracting the sections of the sentence, which are labeled by these sublabels.

    parameters:
        event_label_group: list of event labels of the same type
        attribute -- either "Variable" or "Condition"
        sentence -- natural language sentence to which the labels apply

    returns:
        attribute -- a string extracted from the sections of the sentence covered by the attribute labels of the event label group
        None -- if the event label group contains no sub labels for the attribute"""

    node_attribute_values: list[str] = []
    for candidate_label in event_label_group:
        value = candidate_label.get_attribute(attribute, sentence)
        if value != None:
            node_attribute_values.append(value)

    if len(node_attribute_values) > 0:
        return " ".join(node_attribute_values)
    return None
