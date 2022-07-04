from dataclasses import dataclass, field

@dataclass
class Label:
    id: str
    name: str
    begin: int
    end: int

@dataclass
class SubLabel(Label):
    parent: 'EventLabel' = field(default=None, init=False)

    def __repr__(self):
        return f'({self.id})'

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

    def add_child(self, label: SubLabel):
        self.children.append(label)
        label.parent = self

    def set_successor(self, successor: 'EventLabel', junctor: str):
        neighbor = Neighbor(origin=self, target=successor, junctor=junctor)
        self.successor = neighbor
        successor.predecessor = neighbor
    
    def get_attribute(self, attribute: str, sentence: str) -> str:
        eligible_sublabels = [sublabel for sublabel in self.children if sublabel.name == attribute]

        if len(eligible_sublabels) >= 1:
            return " ".join([sentence[l.begin:l.end] for l in eligible_sublabels])
        return None
    
    
    def __repr__(self):
        return f'({self.id})'