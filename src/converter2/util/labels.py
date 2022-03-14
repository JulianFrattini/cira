from typing import List

from converter2.util.sentence import Sentence

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
    
    def verbatim(self, sentence: Sentence):
        return sentence.getText()[self.begin:self.end]

    def isCausal(self):
        return self.name.startswith('Cause') or self.name.startswith('Effect')

    def isConjunction(self):
        return self.name.startswith('Conjunction') or self.name.startswith('Disjunction')

    def isType(self, type: str):
        return self.name.startswith(type)

    def isInRange(self, start: int, stop: int):
        return self.begin >= start and self.end <= stop

    def __str__(self):
        return f'[{self.begin}> {self.name} <{self.end}]'

# convert a list of json labels into a list of labels using the Label class
def fromJson(labels):
    result = []
    for label in labels:
        result.append(Label(id=label['id'], name=label['label'], begin=label['begin'], end=label['end']))
    return result

# convert a list of labels into a dict, where each causal label name is associated with all of its labels
def mapCausalLabels(labels: List[Label], justCauses: bool=False):
    # get all labels that are causal (causes and effects)
    causalLabels = list(filter(lambda l: (l.isCausal() if not justCauses else l.isType('Cause')), labels))
    # identify all unique label names
    uniqueNames = set(map(lambda l: l.getName(), causalLabels))
    # sort the names alphabetically
    names = sorted(list(uniqueNames))

    # associate each name to all labels with the same name
    result = {}
    for name in names:
        result[name] = list(filter(lambda l: l.isType(name), labels))

    return result

# find a conjunction between two lists of labels, where each list is associated to one node name
def conjunctionsBetween(one: List[Label], two: List[Label], all: List[Label]):
    begin = (sorted(one, key=(lambda l: l.getEnd())))[0].getEnd()
    end = (sorted(two, key=(lambda l: l.getBegin())))[0].getBegin()

    conjunctions = list(filter(lambda l: l.isConjunction(), all))
    for conjunction in conjunctions: 
        if conjunction.isInRange(begin, end):
            print(f'{conjunction} is between the two labels')