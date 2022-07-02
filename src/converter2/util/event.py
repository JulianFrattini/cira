from typing import List
from .labels import Label, EventLabel

class Event:
    def __init__(self, name: str, labels: List[EventLabel]):
        self.name = name
        self.labels = labels

        self.predecessor = None
        self.successor = None
    
    def getName(self):
        return self.name

    def getLabels(self):
        return self.labels

    # predecessor and successors
    def getPredecessor(self):
        return self.predecessor

    def setPredecessor(self, predecessor: 'Event'):
        self.predecessor = predecessor
    
    def getSuccessor(self):
        return self.successor

    def setSuccessor(self, successor: 'Event'):
        self.successor = successor

    def getVariable(self):
        variables = []
        for label in self.labels:
            varLabels = label.getChildren(type='variable')
            for varLabel in varLabels:
                variables.append(varLabel.getText())

        if len(variables) > 0:
            return " ".join(variables)
        else:
            eligibleNeighbors = self.getNeighborsByDegreeOfRelation(preferBacktracking=True)

            for event in eligibleNeighbors:
                variable = event.getVariable()
                if variable != None:
                    return variable

        return None
    
    def isCause(self):
        return self.name.startswith('Cause')

    def getNeighborsByDegreeOfRelation(self, preferBacktracking: bool):
        """Generate an ordered list of neighboring events
        """
        result = []

        candidate = self.predecessor if preferBacktracking else self.successor
        while candidate != None:
            result.append(candidate)
            candidate = candidate.getPredecessor() if preferBacktracking else candidate.getSuccessor()

        return result

    def __str__(self):
        result = f'{self.name}: {list(map(lambda label: str(label), self.labels))}'
        if self.predecessor:
            result = result + f' (pre: {self.predecessor.getName()})'
        if self.successor:
            result = result + f' (post: {self.successor.getName()})'
        return result

class EventList:
    def __init__(self, labels: List[Label]):
        self.events = []

        # get all labels that are causal (causes and effects)
        eventLabels = list(filter(lambda l: l.isCausal(), labels))
        # identify all unique label names
        uniqueEventNames = set(map(lambda l: l.getName(), eventLabels))
        # sort the names alphabetically
        eventNames = sorted(list(uniqueEventNames))

        predecessor = None
        for eventName in eventNames:
            # get all event labels that are associated to this event (multiple, if an event is split)
            relevantLabels = list(filter(lambda label: label.getName() == eventName, eventLabels))
            # create an event from these labels
            event = Event(name=eventName, labels=relevantLabels)
            # for all causes, if this is not the first cause: define the predecessors and successors
            if predecessor is not None: #and eventName.startswith('Cause'):
                predecessor.setSuccessor(successor=event)
                event.setPredecessor(predecessor=predecessor)
            predecessor = event

            self.events.append(event)

    def getEvents(self, ce: str=None):
        if ce and ce == 'causes':
            return list(filter(lambda event: event.getName().startswith('Cause'), self.events))
        elif ce and ce == 'effects':
            return list(filter(lambda event: event.getName().startswith('Effect'), self.events))
        return self.events 

    # find a conjunction between two lists of labels, where each list is associated to one node name
    def getJunctorsBetweenEvents(self, one: Event, two: Event, labels: List[Label]):
        result = []

        begin = (sorted(one.getLabels(), key=(lambda l: l.getEnd())))[0].getEnd()
        end = (sorted(two.getLabels(), key=(lambda l: l.getBegin())))[0].getBegin()

        junctors = list(filter(lambda l: l.isJunctor(), labels))
        for junctor in junctors: 
            if junctor.isInRange(begin, end):
                result.append(junctor)

        return result

    def __str__(self):
        result = ""
        for event in self.events:
            result = result + str(event) + '\n'
        return result