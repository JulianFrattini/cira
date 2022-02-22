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
    
    def verbatim(self, sentence: Sentence):
        return sentence.getText()[self.begin:self.end]

    def isCausal(self):
        return self.name.startswith('Cause') or self.name.startswith('Effect')

    def isType(self, type: str):
        return self.name.startswith(type)

    def isInRange(self, start: int, stop: int):
        return self.begin >= start and self.end <= stop

    def __str__(self):
        return f'[{self.begin}> {self.name} <{self.end}]'

def fromJson(labels):
    result = []
    for label in labels:
        result.append(Label(id=label['id'], name=label['label'], begin=label['begin'], end=label['end']))
    return result

def mapCausalLabels(labels: List[Label]):
    causalLabels = list(filter(lambda l: l.isCausal(), labels))
    uniqueLabels = set(map(lambda l: l.getName(), causalLabels))

    result = {}
    for label in uniqueLabels:
        result[label] = list(filter(lambda l: l.isType(label), labels))

    return result
