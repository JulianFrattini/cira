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

    def base_equals(self, other) -> bool:
        return self.name == other.name and self.begin == other.begin and self.end == other.end

@dataclass
class SubLabel(Label):
    parent: 'EventLabel' = field(default=None, init=False)

    def __repr__(self) -> str:
        return super().__str__()

    def __eq__(self, other) -> bool:
        if type(other) != SubLabel:
            return False

        if (self.parent == None) != (other.parent == None):
            return False
        else:
            if self.parent != None and other.parent != None:
                parent_eq = self.parent.base_equals(other=other.parent)
                if not parent_eq:
                    return False
                    
        return self.base_equals(other)
        

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

    def __eq__(self, other) -> bool:
        if type(other) != EventLabel:
            return False

        # check that the children are equivalent
        if len(self.children) != len(other.children):
            return False
        else:
            # check that every child is contained in the other object
            child_equivalents = [[oc for oc in other.children if child.base_equals(oc)] for child in self.children]

            # check that every child has exactly one equivalent
            child_equivalent_lengths_unqeual_one = [ce for ce in child_equivalents if len(ce)!=1]
            if len(child_equivalent_lengths_unqeual_one) > 0:
                return False

            child_equivalents = set([ce[0].id for ce in child_equivalents])
            if len(child_equivalents) != len(self.children):
                return False

        return self.base_equals(other)
    
    def __str__(self):
        return super().__str__()

    def __repr__(self):
        children = " ".join([child.__repr__() for child in self.children])
        neighbor = f' ({self.successor.junctor} {self.successor.target.id})' if self.successor != None else ""
        return f'[{self.begin}> ({self.id}) {self.name} {neighbor}: {children} <{self.end}]'

def from_dict(serialized: list[dict]) -> list[Label]:
    labels: list[Label] = []

    # differentiate the label type by the attributes of the serialized labels
    for ser in serialized:
        if 'children' in ser.keys():
            labels.append(EventLabel(id=ser['id'], name=ser['name'], begin=ser['begin'], end=ser['end']))
        else:
            labels.append(SubLabel(id=ser['id'], name=ser['name'], begin=ser['begin'], end=ser['end']))

    # connect parents with their children
    for parent in [label for label in labels if type(label)==EventLabel]:
        child_ids = get_serialized_label_by_id(serialized, parent.id)['children']
        for cid in child_ids:
            child = get_label_by_id(labels, cid)
            parent.add_child(child)

    return labels

def get_serialized_label_by_id(serialized: list[dict], id: str) -> dict:
    return [label for label in serialized if label['id']==id][0]

def get_label_by_id(labels: list[Label], id: str) -> Label:
    return [label for label in labels if label.id==id][0]