from converter.util.sentence import Sentence

min_event_index = 1
max_event_index = 3

class Node:
    def __init__(self, var: str="", cond: str="", labels=None, type: str=None, varassumed: bool = False, condassumed: bool = False):
        if var and cond:
            self.intermediate = False
            self.variable = var
            self.condition = cond
            self.labels = labels
        else: 
            self.intermediate = True
            self.type = type
        
        self.incomingConnections = []
        self.outgoingConnections = []
        self.variableassumed = varassumed
        self.conditionassumed = condassumed

    def getLabels(self):
        return self.labels

    def isCauseNode(self):
        if self.isIntermediate():
            return False
        return self.labels[0]['label'].startswith('Cause')

    def isEffectNode(self):
        if self.isIntermediate():
            return False
        return self.labels[0]['label'].startswith('Effect')

    def isIntermediate(self):
        return self.intermediate

    def getConnections(self, incoming: bool=True):
        if incoming:
            return self.incomingConnections
        else:
            return self.outgoingConnections

    def getType(self):
        return self.type

    def __str__(self):
        if self.intermediate:
            return self.type
        else:
            return f"[{self.variable}].({self.condition})"



def generate_node(eventlabel, causal_labels, alllabels, sentence: Sentence):
    variable = obtain_event_attribute(eventlabel, causal_labels, alllabels, sentence, "Variable", "it")
    condition = obtain_event_attribute(eventlabel, causal_labels, alllabels, sentence, "Condition", "is present")

    node = Node(
        var=variable['value'], 
        cond=condition['value'], 
        labels=causal_labels[eventlabel], 
        varassumed=variable['assumed'],
        condassumed=condition['assumed']
    )

    return node

# obtain either the variable or the condition of an event
def obtain_event_attribute(eventlabel, causal_labels, alllabels, sentence: Sentence, attribute: str, default: str):
    value = default
    assumed = False

    # obtain the order of events in which the algorithm should look for the attribute
    event_order = generate_label_order(eventlabel, causal_labels, attribute)
    for event in event_order:
        # get all labels associated to this event
        eventlabels = causal_labels[event]
        # attempt to find the attribute in this event
        attribute_value = find_attribute_in_event(eventlabels, alllabels, sentence, attribute)
        if attribute_value != None:
            value = attribute_value
            # if the value has been obtained from any event other than the original one, flag it as an assumption
            if event != eventlabel:
                assumed = True
            break

    result = {
        'value': value,
        'assumed': assumed
    }
    return result

# generate the order of events, in which the algorithm should look for Variable and Condition
def generate_label_order(current_label, causal_labels, attribute: str):
    # always begin with the initial event itself: in the best (and normal) case, the Variable and Condition is contained in the event label itself
    events = [current_label]

    event_type = current_label[:-1]
    opposite_event_type = 'Effect' if event_type == 'Cause' else 'Cause'
    current_index = int(current_label[-1:])

    # define the ranges of events, in which the algorithm shall search for an attribute if it cannot be found in the initial event
    ranges = [range(current_index-1, min_event_index-1, -1), range(current_index+1, max_event_index+1)]
    # for variables, prioritize looking into prior nodes; for conditions, prioritize looking into subsequent nodes
    if attribute == 'Condition':
        ranges = [ranges[1], ranges[0]]
    # add each of the nodes to the list of eligible events in their respective order
    for rng in ranges:
        for index in rng:
            if (event_type+str(index)) in causal_labels.keys():
                events.append(event_type + str(index))
    # finally, take into consideration the other event types
    for index in range(min_event_index, max_event_index+1):
        if (opposite_event_type + str(index)) in causal_labels.keys():
            events.append(opposite_event_type + str(index))

    return events

# attempt to find an attribute ('Variable', or 'Condition') in a given event (Cause1, Cause2, Cause3, Effect1, Effect2, Effect3)
def find_attribute_in_event(eventlabels, alllabels, sentence: Sentence, attribute: str):
    eligible_labels = sentence.get_encompassed_labels(alllabels, attribute, eventlabels)
    value = None

    if len(eligible_labels) == 1:
        # there is exactly one label of type attribute encompassed by all of the event labels associated to this eventlabel
        label = eligible_labels[0]
        value = sentence.get_text()[label['begin']:label['end']]
    elif len(eligible_labels) > 1:
        # there are more than one label of type attribute encompassed by all of the event labels associated to this eventlabel
        value = ' '.join(map(lambda label: sentence.get_text()[label['begin']:label['end']], eligible_labels))
    # if there are no labels of type attribute encompassed by the event labels, simply return None
    return value