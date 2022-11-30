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

    def to_dict(self) -> dict:
        """Serialize a Label object to a standard dictionary, which gets rid of all cyclic dependencies and replaces them by references.

        returns: label serialized as a dictionary"""
        dictified: dict = {
            'id': self.id,
            'name': self.name,
            'begin': int(self.begin),
            'end': int(self.end)
        }
        return dictified

    def base_equals(self, other: 'Label') -> bool:
        """Basic equivalence method that checks that the name, begin, and end of another label equals this label's attributes. The id is purposefully ignored.

        parameters:
            other -- Candidate label to compare this label to

        returns: True if the name, begin, and end attribute of the candidate is equivalent to this ones"""
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
        """Serialize a Label object to a standard dictionary, which gets rid of all cyclic dependencies and replaces them by references.

        returns: label serialized as a dictionary"""
        parent_dict: dict = super().to_dict()
        dictified: dict = {
            'parent': None if self.parent==None else self.parent.id
        }
        return parent_dict | dictified

@dataclass
class Neighbor:
    origin: 'EventLabel' = field(default=None)
    target: 'EventLabel' = field(default=None)
    junctor: str = None # AND, OR, POR, MERGE

@dataclass
class EventLabel(Label):
    children: list[SubLabel] = field(default_factory=list, init=False)
    predecessor: Neighbor = field(default=None, init=False)
    successor: Neighbor = field(default=None, init=False)

    def is_cause(self) -> bool:
        """Determines whether this event represents a cause.

        returns: True, if the name of the label begins with 'Cause'"""
        return self.name.startswith('Cause')

    def add_child(self, child: SubLabel):
        """Add a SubLabel as a child of this label. The child should be encompassed by the parent label.

        paramters:
            child -- SubLabel to add to this label"""
        self.children.append(child)
        child.parent = self

    def set_successor(self, successor: 'EventLabel', junctor: str):
        """Set the successor of this event, which is the subsequent event in the list of events (e.g., Cause2 follows Cause1). This will automatically set the predecessor of the successor to this event.

        parameters:
            successor -- EventLabel succeeding this label
            junctor -- either 'AND' or 'OR' depending on how the two events are connected
        """
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
        """Serialize a Label object to a standard dictionary, which gets rid of all cyclic dependencies and replaces them by references.

        returns: label serialized as a dictionary"""
        parent_dict: dict = super().to_dict()
        dictified: dict = {
            'successor': None if self.successor == None else {
                'id': self.successor.target.id,
                'junctor': self.successor.junctor},
            'children': [child.id for child in self.children]
        }
        return parent_dict | dictified

    def __eq__(self, other) -> bool:
        """Deep equivalence method comparing this object with another object. An object that is to be identified as equivalent to this object has to (1) also be of type EventLabel, (2) have equal children, (3) have equal successors and predecessors, and (4) have equal base values. The equivalence check has a depth of 1, i.e., all connected objects are only checked for equivalent base values (e.g., successors are only compared via base_equals, not via __eq__, as this would cause a cycle).

        parameters:
            other -- candidate object to compare this object to

        returns: True, if the other object is equivalent to this one."""
        if type(other) != EventLabel:
            return False

        # check that the children are equivalent
        if len(self.children) != len(other.children):
            return False
        else:
            # check that every child is contained in the other object
            child_equivalents = [[oc for oc in other.children if child.base_equals(oc)] for child in self.children]

            # check that every child has exactly one equivalent
            child_equivalent_lengths_unqeual_one = [ce for ce in child_equivalents if len(ce) != 1]
            if len(child_equivalent_lengths_unqeual_one) > 0:
                return False

            child_equivalents = set([ce[0].id for ce in child_equivalents])
            if len(child_equivalents) != len(self.children):
                return False

        # check that the successor and predecessor are equivalent
        for cessor,eqtarget in [('predecessor', 'origin'), ('successor', 'target')]:
            sces: Neighbor = getattr(self, cessor)
            oces: Neighbor = getattr(other, cessor)

            if (sces==None) != (oces == None):
                return False
            else:
                if sces!=None and oces != None:
                    if sces.junctor != oces.junctor:
                        return False
                    if not getattr(sces,eqtarget).base_equals(getattr(oces,eqtarget)):
                        return False

        return self.base_equals(other)

    def __str__(self):
        return super().__str__()

    def __repr__(self):
        children = " ".join([child.__repr__() for child in self.children])
        neighbor = f' ({self.successor.junctor} {self.successor.target.id})' if self.successor != None else ""
        return f'[{self.begin}> ({self.id}) {self.name} {neighbor}: {children} <{self.end}]'


def from_dict(serialized: list[dict]) -> list[Label]:
    """Deserialization method converting a list of labels that are represented by dictionaries back into a list of of actual EventLabel and SubLabel objects. This process restores the cyclic relationships from the references in the dictionaries (i.e., recovers both parent-child and predecessor-successor relationships).

    parameters:
        serialized -- list of labels serialized to dictionaries

    returns: list of actual Labels"""

    labels: list[Label] = []

    # differentiate the label type by the attributes of the serialized labels
    for ser in serialized:
        if 'children' in ser.keys():
            labels.append(EventLabel(id=ser['id'], name=ser['name'], begin=ser['begin'], end=ser['end']))
        else:
            labels.append(SubLabel(id=ser['id'], name=ser['name'], begin=ser['begin'], end=ser['end']))

    # connect parents with their children
    for parent in [label for label in labels if type(label) == EventLabel]:
        child_ids = get_serialized_label_by_id(serialized, parent.id)['children']
        for cid in child_ids:
            child = get_label_by_id(labels, cid)
            parent.add_child(child)

    # connect events with their neighbors
    for event in [label for label in labels if type(label) == EventLabel]:
        successor_info = get_serialized_label_by_id(serialized, event.id)['successor']
        if successor_info != None:
            successor = get_label_by_id(labels, successor_info['id'])
            junctor = successor_info['junctor']
            event.set_successor(successor, junctor)

    return labels


def get_serialized_label_by_id(serialized: list[dict], id: str) -> dict:
    """Obtain a label from a list of serialized labels by its id

    parameters:
        serialized -- list of labels serialized to dictionaries
        id -- identifier of the requested dict labels

    returns:
        label -- dictionary representing the label if it exists,
        None -- otherwise"""
    candidates = [label for label in serialized if label['id'] == id]
    if len(candidates) == 0:
        return None
    if len(candidates) > 1:
        print(f'Warning: searching for label {id} in {serialized} yielded mulitple results')
    return candidates[0]


def get_label_by_id(labels: list[Label], id: str) -> Label:
    """Obtain a label from a list of labels by its id

    parameters:
        labels -- list of labels
        id -- identifier of the requested dict labels

    returns:
        label -- label with the requested id if it exists,
        None -- otherwise"""
    candidates = [label for label in labels if label.id == id]
    if len(candidates) == 0:
        return None
    if len(candidates) > 1:
        print(f'Warning: searching for label {id} in {labels} yielded mulitple results')
    return candidates[0]

def get_label_by_type_and_position(labels: list[Label], type: str, begin: int, end: int) -> Label:
    """Obtain a label from a list of label by both its type and its position (begin and end).
    
    parameters:
        labels -- list of labels
        type -- the name of the label (e.g., 'Condition', 'Negation', etc.)
        begin -- the starting index of the label in the sentence
        end -- the ending index of the label in the sentence
        
    returns:
        label -- label with the requested id if it exists,
        None -- otherwise"""
    candidates = [label for label in labels if (label.name==type and label.begin==begin and label.end==end)]
    if len(candidates) == 0:
        return None
    if len(candidates) > 1:
        print(f'Warning: searching for a {type} label at position [{begin}, {end}] yielded multiple results.')
    return candidates[0]