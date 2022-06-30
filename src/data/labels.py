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