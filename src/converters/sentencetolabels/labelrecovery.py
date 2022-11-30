import re

from src.data.labels import Label, EventLabel, SubLabel
from src.data.labels import get_label_by_type_and_position

def recover_labels(sentence: str, labels: list[Label]) -> list[Label]:
    """The capabilities of the BERT-based sentence labeler are limited. Because some sentence structures are more rare than others (e.g., exceptive clauses), the labeler might miss important information. This method manually recovers certain labels according to specific patterns and updates the list of labels currently associated with the sentence
    """
    # recover missing labels
    for add_labels in [label_exceptive_clauses]:
        labels += add_labels(sentence, labels)

    return labels 

EXCEPTIVE_CLAUSES = ['unless']
def label_exceptive_clauses(sentence: str, labels: list[Label]) -> list[SubLabel]:
    """Identify all instances of exceptive clauses (determined by the list of words above) that have not been labeled. Because exceptive clauses like this are very rare they have apparently not been picked up by the BERT-based labeler. Because they convey important information ("Unless A then B" translates to "If not A then B") they need to be recovered. This method generates a negation for each exceptive clause that does not yet contain one.
    
    parameters:
        sentence -- natural language sentence
        labels -- list of labels already associated with the sentence
        
    returns: list of labels for previously unlabeled exceptive clauses"""

    additional_labels: list[SubLabel] = []

    exceptive_instances = []
    for exclause in EXCEPTIVE_CLAUSES:
        iter = re.finditer(exclause, sentence.lower())
        exceptive_instances += [m.span() for m in iter]

    for index, instance in enumerate(exceptive_instances):
        label = get_label_by_type_and_position(labels, type='Negation', begin=instance[0], end=instance[1])
        if label == None:
            additional_labels.append(SubLabel(id=f'AEX{index}', name='Negation', begin=instance[0], end=instance[1]))

    return additional_labels