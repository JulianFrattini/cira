min_event_index = 1
max_event_index = 3

def transform(sentence, labels):
    # get all causal labels
    #causal_labels = get_causal_labels(labels)
    causal_labels = sentence.get_causal_labels()

    # generate a CEG node for each label
    #nodes = generate_nodes(causal_labels, labels, sentence)

    # generate the edges between the nodes
    #ceg = generate_edges(nodes, labels, sentence)

    #return ceg
    return None


def get_labels_of_type(labels, type: str):
    relevant_labels = []
    for label in labels:
        if label['label'].startswith(type):
            relevant_labels.append(label)
    return relevant_labels

def generate_nodes(causal_labels, alllabels, sentence: str):
    nodes = []
    for eventlabel in causal_labels.keys():
        node = generate_node(eventlabel, causal_labels, alllabels, sentence)
        nodes.append(node)
    return nodes

def generate_node(eventlabel, causal_labels, alllabels, sentence: str):
    variable = obtain_event_attribute(eventlabel, causal_labels, alllabels, sentence, "Variable", "it")
    condition = obtain_event_attribute(eventlabel, causal_labels, alllabels, sentence, "Condition", "is present")

    node = {
        'variable': variable['value'],
        'condition': condition['value'],
        'label': causal_labels[eventlabel],
        'incomingConnections': [],
        'outgoingConnections': [],
        'variableassumed': variable['assumed'],
        'conditionassumed': condition['assumed']
    }

    return node

# obtain either the variable or the condition of an event
def obtain_event_attribute(eventlabel, causal_labels, alllabels, sentence: str, attribute: str, default: str):
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
def find_attribute_in_event(eventlabels, alllabels, sentence: str, attribute: str):
    eligible_labels = get_encompassed_labels(alllabels, attribute, eventlabels)
    value = None

    if len(eligible_labels) == 1:
        # there is exactly one label of type attribute encompassed by all of the event labels associated to this eventlabel
        label = eligible_labels[0]
        value = sentence[label['begin']:label['end']]
    elif len(eligible_labels) > 1:
        # there are more than one label of type attribute encompassed by all of the event labels associated to this eventlabel
        value = ' '.join(map(lambda label: sentence[label['begin']:label['end']], eligible_labels))
    # if there are no labels of type attribute encompassed by the event labels, simply return None
    return value

def generate_edges(nodes, labels, sentence):
    edges = []
    finalnodes = []

    causenodes = list(filter(lambda node: node['label'][0]['label'].startswith('Cause'), nodes))
    final_cause_node = None

    additional_negations = []

    # resolve junctors
    if len(causenodes) == 1:
        # if there is only one cause node there is no need for resolving junctors
        final_cause_node = causenodes[0]
        finalnodes.append(final_cause_node)
    else: 
        # find all explicit junctors
        causejunctors = []
        # keep track of priorizations that break the standard precedence rule (e.g.: in "e1 and either e2 and e3", the disjunction has higher precedence than the conjunction)
        priorityjunctors = []
        priorityjunctor = ""

        for i in range(0, len(causenodes)-1):
            # get the indices of the space between the two adjacent cause nodes
            end_of_cause_1 = causenodes[i]['label'][-1]['end']
            begin_of_cause_2 = causenodes[i+1]['label'][0]['begin']

            # count the occurrences of conjunctions and disjunctions in this space
            nconjunctions = len(get_labels_inbetween(labels, 'Conjunction', end_of_cause_1, begin_of_cause_2))
            ndisjunctions = len(get_labels_inbetween(labels, 'Disjunction', end_of_cause_1, begin_of_cause_2))

            # determine the junctor at the index position based on the number of occurrences
            if nconjunctions > 0 and ndisjunctions == 0:
                causejunctors.insert(i, 'AND')
                # reset the priority propagation
                if priorityjunctor == 'OR':
                    priorityjunctor = ''
            elif nconjunctions == 0 and ndisjunctions > 0:
                causejunctors.insert(i, 'OR')
                # propagate the priority if it exists
                if priorityjunctor == 'OR':
                    priorityjunctors.append(i)
            elif nconjunctions > 0 and ndisjunctions > 0:
                causejunctors.insert(i, 'AND')
                priorityjunctor = 'OR'
            else:
                causejunctors.insert(i, 'missing')
                if priorityjunctor == 'OR':
                    priorityjunctors.append(i)

        # if the last junctor between causes is missing, it is likely that all junctors are implicit (hence assume a conjunction)
        if causejunctors[-1] == 'missing':
            causejunctors[-1] = 'AND'
        # assume all implicit junctors by using the subsequent junctor
        for index in range(len(causejunctors)-2, 0, -1):
            if causejunctors[index] == 'missing':
                causejunctors[index] = causejunctors[index+1]

        additional_negations = identify_additional_negations(labels, nodes, causejunctors, sentence)

        # construct intermediate nodes
        while len(causejunctors) > 0:
            # standard precedence: conjunctions bind stronger than disjunctions
            current_junctor = 'AND' if causejunctors.index('AND') != -1 else 'OR'
            index = causejunctors.index(current_junctor)
            # in case of prioritized junctors, select those:
            if len(priorityjunctors) > 0:
                index = priorityjunctors.pop()
                current_junctor = causejunctors[index]

            # create an indermediate node with the current junctor
            intermediatenode = {
                'variable': '',
                'condition': '',
                'type': current_junctor,
                'incomingConnections': [],
                'outgoingConnections': [],
                'variableassumed': False,
                'conditionassumed': False
            }

            # create an edge from the two adjacent nodes to the new intermediate node
            negated = False
            if not is_intermediate(causenodes[index]):
                negated = is_negated(causenodes[index], labels, additional_negations)
            edges.append(create_edge(causenodes[index], intermediatenode, negated))
            if not is_intermediate(causenodes[index+1]):
                negated = is_negated(causenodes[index+1], labels, additional_negations)
            edges.append(create_edge(causenodes[index+1], intermediatenode, negated))

            finalnodes.append(causenodes[index])
            finalnodes.append(causenodes[index+1])

            causenodes[index:index+2] = [intermediatenode]
            causejunctors.pop(index)
        
        # add the final cause node to the list of final nodes and declare it as a root node
        final_cause_node = causenodes[0]
        finalnodes.append(causenodes[0])

        # collapse all intermediate nodes where possible (chained intermediates of the same type)
        final_cause_node = collapse_intermediate_nodes(final_cause_node, finalnodes, edges)

    effectnodes = list(filter(lambda node: node['label'][0]['label'].startswith('Effect'), nodes))
    finalnodes = finalnodes + effectnodes

    # if the cause nodes consist of only one single node (and no intermediates), double negations must be resolved manually
    resolvenegation = False
    if not is_intermediate(final_cause_node):
        if is_negated(final_cause_node, labels, additional_negations):
            resolvenegation = True

    # create edges from the final causal node to all effect nodes
    for effect in effectnodes:
        is_node_negated = is_negated(effect, labels, additional_negations)
        edges.append(create_edge(final_cause_node, effect, (not is_node_negated if resolvenegation else is_node_negated)))

    ceg = {
        'nodes': finalnodes,
        'edges': edges
    }

    return ceg

def identify_additional_negations(labels, nodes, causejunctors, sentence):
    # filter labels are already within a cause or effect node
    naked_negations = get_naked_negations(labels, nodes, sentence)

    # determine which of the causal nodes are additionally negated by the unhandled negations
    negated_nodes = []
    if len(naked_negations) > 0:
        causenodes = list(filter(lambda node: (node['label'][0]['label'].startswith('Cause'), nodes)))

        for negation in naked_negations:
            next_causal_node = get_next_causal_node(negation, causenodes)
            negatedindex = causenodes.index(next_causal_node)

            negated_nodes.push(next_causal_node)
            while causejunctors[negatedindex] == 'AND':
                negatedindex += 1
                negated_nodes.append(causenodes[negatedindex])
    
    return negated_nodes


def get_naked_negations(labels, nodes, sentence):
    causal_nodes = list(filter(lambda node: (node['label'][0]['label'].startswith('Cause') or node['label'][0]['label'].startswith('Effect')), nodes))
    # determine the covered space, i.e., the ranges, which are already covered by causal nodes
    covered_space = []
    for node in causal_nodes:
        covered_space = covered_space + list(map(lambda label: [label['begin'], label['end']], node['label']))
    # discover all negations between those covered spaces: those are the negations that are not directly associated to an event
    unhandled_negations = []
    for index in range(0, len(covered_space)+1):
        begin = 0 if index == 0 else covered_space[index-1][1]
        end = len(sentence)+1 if index == len(covered_space) else covered_space[index][0]
        unhandled_negations = unhandled_negations + get_labels_inbetween(labels, 'Negation', begin, end)
    return unhandled_negations

def get_next_causal_node(label, causalnodes):
    for node in causalnodes:
        if label['end'] <= node['label'][0]['begin']:
            return node
    return None

def get_encompassed_labels(alllabels, type: str, encompassing):
    relevant_labels = []
    for label in encompassing:
        relevant_labels = relevant_labels + get_labels_inbetween(alllabels, type, label['begin'], label['end'])
    return relevant_labels

def get_labels_inbetween(alllabels, type, begin: int, end: int):
    relevant_labels = []
    for label in alllabels:
        if label['begin'] >= begin and label['end'] <= end and label['label'] == type:
            relevant_labels.append(label)
    return relevant_labels

def is_intermediate(node):
    return node['variable'] == '' and node['condition'] == ''

def is_negated(node, labels, additionalnegations):
    negationswithin = get_encompassed_labels(labels, 'Negation', node['label'])
    #if additionalnegations.index(node) == -1:
    if node in additionalnegations:
        # if the node is not already negated from an outside node (e.g., exceptive clause), return true if the number of negations is uneven (to deal with double negatives)"
        return len(negationswithin) > 0 and len(negationswithin)%2 != 0
    else:
        # if the node is not already negated from an outside node (e.g., exceptive clause), invert the result
        return not (len(negationswithin) > 0 and len(negationswithin)%2 != 0)

def create_edge(source, target, negate: bool):
    edge = {
        'source': source,
        'target': target,
        'negate': negate
    }

    source['outgoingConnections'].append(edge)
    target['incomingConnections'].append(edge)

    return edge

def collapse_intermediate_nodes(currentnode, nodes, edges):
    if is_intermediate(currentnode):
        children = get_child_nodes(currentnode, edges)

        # get all child nodes which are also intermediate nodes
        child_intermediates = list(filter(lambda child: is_intermediate(child), children))

        for child_intermediate in child_intermediates:
            # recursively collapse child nodes first
            child_intermediate = collapse_intermediate_nodes(child_intermediate, nodes, edges)

            # identify child nodes with the same type (conjunction/disjunction) as the current node
            if child_intermediate['type'] == currentnode['type']:
                # rewire the edges between the grandchildren and the child to the parent node
                for grandchild in get_child_nodes(child_intermediate, edges):
                    edge = get_edge_between(grandchild, child_intermediate, edges)
                    print('edge between ' + str(edge['source']['variable']) + ' and ' + str(edge['target']['variable']))
                    edge['target'] = currentnode
                    currentnode['incomingConnections'].append(edge)

                # delete the obsolete edge from the child node to the parent node
                remove_edge(get_edge_between(child_intermediate, currentnode, edges), edges)
                # delete the obsolete intermediate node
                nodes.remove(child_intermediate)
    return currentnode


def get_child_nodes(parent, edges):
    parenting = list(filter(lambda edge: edge['target'] == parent, edges))
    return list(map(lambda edge: edge['source'], parenting))

def get_edge_between(node1, node2, edges): 
    outgoing = list(filter(lambda edge: edge['source'] == node1 and edge['target'] == node2, edges))
    if len(outgoing) == 1:
        return outgoing[0]
    return None

def remove_edge(edge, edges):
    edge['source']['outgoingConnections'].remove(edge)
    edge['target']['incomingConnections'].remove(edge)
    edges.remove(edge)

    return edges