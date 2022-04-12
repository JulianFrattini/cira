from .util.sentence import Sentence
from .util.labels import Label
from .util.event import Event, EventList
from .util.graph import Node, EventNode, IntermediateNode, Graph

def transform(sentence: Sentence):
    # get all causal nodes
    labels = sentence.getLabels()
    
    # generate the events from the labels and filter for all cause events
    eventlist = EventList(labels)
    causes = eventlist.getEvents(ce='causes')

    # generate nodes for each cause
    causenodes = {}
    for cause in causes:
        causenodes[cause.getName()] = EventNode(cause=True, variable=cause.getVariable())
    
    # resolve junctors between the causes
    if len(causes) > 1:
        constructIntermediateNodes(causes, eventlist, causenodes, labels)
        unifyIntermediates(causenodes)

    root = causenodes['Cause1'].getRoot()

    # add effect nodes to the graph
    effectNodes = []
    for effect in eventlist.getEvents(ce='effects'):
        effectNodes.append(EventNode(cause=False, variable=effect.getName()))

    return Graph(rootcause=root, effects=effectNodes)

def constructIntermediateNodes(causes, eventlist, causenodes, labels):
    previousJunctorType = 'Conjunction'
    intermediatenodes = []

    for one, two in zip(causes[::-1][1:], causes[::-1][:-1]):
        # obtain all junctors between the two causes
        junctors = eventlist.getJunctorsBetweenEvents(one, two, labels)

        junctor = None
        if len(junctors) == 1:
            # standard case: there is exactly one junctor between the two 
            junctor = junctors[0].getName()
        elif len(junctors) == 0:
            # implicit case: there is no junctor, hence take the previously defined one
            junctor = previousJunctorType
        previousJunctorType = junctor

        # create the appropriate intermediate node
        children = [causenodes[one.getName()], causenodes[two.getName()]]
        intermediateNode = IntermediateNode((junctor == 'Conjunction'), children=children)
        intermediatenodes.append(intermediateNode)

def unifyIntermediates(causenodes):
    # unify the graph to a common root node
    while len(list(filter(lambda node: len(node.getParents()) > 1, causenodes.values()))) > 0:
        multiparents = list(filter(lambda node: len(node.getParents()) > 1, causenodes.values()))

        # select the first node with more than one parent as an eligible candidate
        candidate = multiparents[0]
        parents = candidate.getParents()

        # identify, if there is at least one disjunction among the parents
        disparents = list(filter(lambda p: not p.isConjunction(), parents))

        if len(disparents) > 0:
            if len(disparents) == len(parents):
                # todo: unify all parents
                break
            else:
                # one disjunction and one conjunction: rewire the relationship between the node and the disjunction to be between the conjunction and disjunction
                disparent = disparents[0]
                conparent = list(filter(lambda p: p.isConjunction(), parents))[0]
                disparent.rewire(origin=candidate, target=conparent)
        else:
            # todo: handle the case with only conjunctions
            break