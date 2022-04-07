from typing import List
from abc import abstractmethod

class Label:
    def __init__(self, id: str, name: str, begin: int, end: int):
        self.id = id
        self.name = name
        self.begin = begin
        self.end = end

    def getName(self):
        return self.name

    def getBegin(self):
        return self.begin

    def getEnd(self):
        return self.end
    
    def verbatim(self, text: str):
        return text[self.begin:self.end]

    #@abstractmethod
    def isCausal(self):
        return False

    def isJunctor(self):
        return self.name.startswith('Conjunction') or self.name.startswith('Disjunction')

    def isType(self, type: str):
        return self.name.startswith(type)

    def isInRange(self, start: int, stop: int):
        return self.begin >= start and self.end <= stop

    def __str__(self):
        return f'[{self.begin}> {self.name} <{self.end}]'

class EventLabel(Label):
    def __init__(self, id: str, name: str, begin: int, end: int, children: List[Label]):
        super().__init__(id, name, begin, end)
        self.children = children

    def isCausal(self):
        return True
        
    def __str__(self):
        result = f'[{self.begin}> {self.name} ({len(self.children)}) <{self.end}]'
        #for child in self.children:
        #    result = result + '\n  - ' + str(child)
        return result

# convert a list of json labels into a list of labels using the Label class
def fromJson(labels: List[object]):
    result = []

    # start py parsing all non-event labels
    for label in filter(lambda l: l['label'] in ['Conjunction', 'Disjunction'], labels):
        result.append(Label(id=label['id'], name=label['label'], begin=label['begin'], end=label['end']))

    # filter for sublabels (variables, conditions, and negations) which are mostly children of events
    sublabels = list(filter(lambda l: l['label'] in ['Variable', 'Condition', 'Negation'], labels))
    events = list(filter(lambda l: l['label'].startswith('Cause') or l['label'].startswith('Effect'), labels))
    for event in events:
        children = []
        for sublabel in filter(lambda sl: sl['begin'] >= event['begin'] and sl['end'] <= event['end'], sublabels):
            children.append(Label(id=sublabel['id'], name=sublabel['label'], begin=sublabel['begin'], end=sublabel['end']))

        result.append(EventLabel(id=event['id'], name=event['label'], begin=event['begin'], end=event['end'], children=children))

    # TODO catch uncontained negations

    return sorted(result, key=(lambda label: label.getBegin()))