from abc import abstractmethod
from dataclasses import dataclass, field

@dataclass
class Label:
    id: str
    name: str
    begin: int
    end: int

    def __str__(self):
        return f'[{self.begin}> ({self.id}) {self.name} <{self.end}]'

    @abstractmethod
    def to_dict(self) -> dict:
        pass

@dataclass
class SubLabel(Label):
    parent: 'EventLabel' = field(default=None, init=False)

    def __repr__(self):
        return super().__str__()

    def to_dict(self) -> dict:
        dictified: dict = {
            'id': self.id,
            'name': self.name,
            'begin': self.begin,
            'end': self.end,
            'parent': None if self.parent==None else self.parent.id
        }
        return dictified

@dataclass
class Neighbor:
    origin: 'EventLabel' = field(default=None)
    target: 'EventLabel' = field(default=None)
    junctor: str = None

@dataclass
class EventLabel(Label):
    children: list[SubLabel] = field(default_factory=list, init=False)
    predecessor: Neighbor = field(default=None, init=False)
    successor: Neighbor = field(default=None, init=False)

    def is_cause(self):
        return self.name.startswith('Cause')

    def add_child(self, child: SubLabel):
        self.children.append(child)
        child.parent = self

    def set_successor(self, successor: 'EventLabel', junctor: str):
        neighbor = Neighbor(origin=self, target=successor, junctor=junctor)
        self.successor = neighbor
        successor.predecessor = neighbor
    
    def get_attribute(self, attribute: str, sentence: str) -> str:
        """Get the verbose attribute of an event
        
        parameters:
            attribute -- either 'Variable' or 'Condition'
            sentence -- verbode sentence
        
        returns: if the event label parents at least one sub label with the given attribute type, a joined string of all parts of the sentence  covered by those labels; None otherwise"""

        eligible_sublabels = [sublabel for sublabel in self.children if sublabel.name == attribute]

        if len(eligible_sublabels) >= 1:
            return " ".join([sentence[l.begin:l.end] for l in eligible_sublabels])
        return None

    def to_dict(self) -> dict:
        dictified: dict = {
            'id': self.id,
            'name': self.name,
            'begin': self.begin,
            'end': self.end,
            'predecessor': None if self.predecessor==None else {
                'id': self.predecessor.origin.id,
                'junctor': self.predecessor.junctor},
            'successor': None if self.successor==None else {
                'id': self.successor.target.id,
                'junctor': self.successor.junctor},
            'children': [child.id for child in self.children]
        }
        return dictified
    
    def __str__(self):
        return super().__str__()

    def __repr__(self):
        children = " ".join([child.__repr__() for child in self.children])
        neighbor = f' ({self.successor.junctor} {self.successor.target.id})' if self.successor != None else ""
        return f'[{self.begin}> ({self.id}) {self.name} {neighbor}: {children} <{self.end}]'