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

@dataclass
class EventLabel(Label):
    children: list[SubLabel] = field(default_factory=list, init=False)
    predecessor: 'EventLabel' = field(default=None, init=False)
    successor: 'EventLabel' = field(default=None, init=False)

    def add_child(self, label: SubLabel):
        self.children.append(label)
        label.parent = self

    def set_successor(self, successor: 'EventLabel'):
        self.successor = successor
        successor.predecessor = self
    
    def get_attribute(self, attribute: str, sentence: str) -> str:
        eligible_sublabels = [sublabel for sublabel in self.children if sublabel.name == attribute]

        if len(eligible_sublabels) >= 1:
            return " ".join([sentence[l.begin:l.end] for l in eligible_sublabels])
        return None