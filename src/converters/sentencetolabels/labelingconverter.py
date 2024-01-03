import re
from dataclasses import dataclass

from torch import Tensor

import src.util.constants as consts
from src.converters.sentencetolabels.labelrecovery import recover_labels
from src.data.labels import EventLabel, Label, SubLabel

TOKEN_PREFIX = 'Ġ'
TOKEN_INIT = '<s>'
TOKENS_END = ['</s>', '<pad>', '<sep>']

@dataclass
class TokenLabel:
    begin: int
    end: int
    event: bool
    name: str

def convert(sentence_tokens: list[str], sentence: str, predictions: Tensor) -> list[Label]:
    """Convert the list of sentence tokens and the list of predictions into a list of label objects

    parameters:
        sentence_tokens -- list of tokens of the labeled sentence (words) as produced by the labeler
        sentence -- actual sentence
        predictions -- matrix of predictions (valid labels for each token)

    returns: list of actual labels on the sentence"""
    # convert the list of sentence tokens, predictions, and labels into a list of token labels, where each token is associated with up to two labels
    token_labels = get_token_labeling(sentence_tokens=sentence_tokens, sentence=sentence, predictions=predictions)

    # merge all adjacent labels
    labels: list[Label] = merge_labels(token_labels=token_labels)

    # connect first-level and second-level labels with each other
    connect_labels(labels)

    # manually recover all missing labels that the labeler was incapable of adding automatically
    labels = recover_labels(sentence, labels)

    return labels

def get_token_labeling(sentence_tokens: list[str], sentence: str, predictions: Tensor) -> list[TokenLabel]:
    """Convert the list of sentence tokens, predictions, and label ids into a list of tokens associated to all available labels

    parameters:
        sentence_tokens -- list of sentence tokens (usually one token per word or special character)
        sentence -- full sentence which comprises of the sentence_tokens
        predictions -- list of predictions for each token, associating each available label with a weight within [0;1]

    returns: list of token labels, containing one object for each token label (max 2 per token)
    """
    token_labels: list[TokenLabel] = []
    cursor = 0

    for token_prediction_idx, token_prediction in enumerate(predictions[0]):
        # get the current token and clean it of the RoBERTa-specific prefix
        token: str = sentence_tokens[token_prediction_idx]
        token = token.replace(TOKEN_PREFIX, "")

        # skip the initializing token
        if token == TOKEN_INIT:
            continue

        # stop once a finalizing token is reached
        if token in TOKENS_END:
            break

        # advance the cursor to the position of this token in the sentence
        advance = position_of_next_token(sentence, cursor, token)
        cursor += advance

        # get all labels associated to a token
        for label_prediction_idx, label_prediction in enumerate(token_prediction):
            if label_prediction != 1:
                continue

            label = consts.LABEL_IDS_VERBOSE[label_prediction_idx]
            if label == consts.NOTRELEVANT:
                continue

            token_labels.append(TokenLabel(
                begin=cursor,
                end=cursor+len(token),
                event = consts.is_event(label),
                name=label))

        # move the cursor to the end of the current token
        cursor += len(token)

    return token_labels

def merge_labels(token_labels: list[TokenLabel]) -> list[Label]:
    """Convert the list of token labels, where every single token is associated to up to two labels, to a list of merged labels, where each label spans all tokens that belong to the same label.

    parameters:
        token_labels -- list of each token within the sentence associated to up to two labels
        labels -- list of used labels in order

    returns:
        list of merged labels
    """
    merged_labels: list[Label] = []
    id_counter = 0
    # keep track of event borders (begin and end of an event label)
    event_borders = []

    for ltype in consts.LABEL_IDS_VERBOSE:
        # get all labels of that type in the list of token labels
        all_of_type = [tl for tl in token_labels if tl.name==ltype]

        # merge adjacent token labels with one exception: if two second-level labels (Variable or Condition) are adjacent, but both belong to two different first-level (event) labels (Cause1/2/3, Event1/2/3), don't merge them
        if len(all_of_type) > 1:
            for index in range(len(all_of_type)-1, 0, -1):
                if all_of_type[index].begin - all_of_type[index-1].end <= 1 and \
                        all_of_type[index].begin not in event_borders and \
                        all_of_type[index-1].end not in event_borders:
                    b = all_of_type.pop(index)
                    a = all_of_type.pop(index-1)
                    merged = TokenLabel(begin=a.begin, end=b.end, event=a.event, name=a.name)
                    all_of_type.insert(index-1, merged)

        for l in all_of_type:
            idv = f'L{id_counter}'
            label: Label = None
            label_trimmed = l.name[:-1]
            if consts.is_event(label_trimmed):
                label = EventLabel(id=idv, name=l.name, begin=l.begin, end=l.end)
                event_borders.extend([l.begin, l.end])
            else:
                label = SubLabel(id=idv, name=l.name, begin=l.begin, end=l.end)
            merged_labels.append(label)
            id_counter += 1

    return merged_labels

def connect_labels(labels: list[Label]) -> None:
    """Connect event labels with their connected child labels and their neighbors

    parameters:
        labels -- list of unconnected labels (both EventLabels and SubLabels)
    """
    event_labels: list[EventLabel] = [label for label in labels if type(label) == EventLabel]

    for event_label in event_labels:
        children = [label for label in labels if (type(label) == SubLabel and label.begin >= event_label.begin and label.end <= event_label.end)]
        for child in children:
            event_label.add_child(child)

    # assign neighboring event labels as predecessor and successor of each other
    event_labels.sort(key=(lambda l: l.begin), reverse=False)
    overruled_precedence = False
    for index, _ in enumerate(event_labels[:-1]):
        junctors: list[SubLabel] = get_junctors_between(labels=labels, first=event_labels[index], second=event_labels[index+1])
        junctor: str = None
        if len(junctors) == 1:
            junctor = consts.AND if junctors[0].name == consts.CONJUNCTION else consts.OR

            if overruled_precedence:
                if junctor == consts.OR:
                    # disjunctions introduced by an overruling precedence get priority
                    junctor = consts.POR
                else:
                    # a conjunction ends the overruling precedence
                    overruled_precedence = False
        elif len(junctors) > 1:
            junctor_names = [junctor.name for junctor in junctors]
            # adapted precedence: in the case of "A and either B or C" the precedence of the disjunction is higher than of the conjunction
            if consts.CONJUNCTION in junctor_names and consts.DISJUNCTION in junctor_names:
                # as a result, this junctor will remain AND, but all following disjunctions will be high-precedence ORs
                junctor = consts.AND
                overruled_precedence = True
        event_labels[index].set_successor(successor=event_labels[index+1], junctor=junctor)


def get_junctors_between(labels: list[Label], first: EventLabel, second: EventLabel) -> list[SubLabel]:
    """Retrieve all junctors between the first and second event label

    parameters:
        labels -- list of all labels
        first -- event label from whose end point the search begins
        second -- event label where the search ends

    returns: all conjunctions and disjunctions between the two event labels"""

    junctors: list[SubLabel] = [label for label in labels if (label.begin >= first.end and label.end <= second.begin and consts.is_junctor(label.name))]

    return junctors

def position_of_next_token(sentence: str, cursor_pos: int, token: str) -> int:
    """Calculate the amount of characters the cursor needs to jump to the next token. The calculation takes into account that certain characters cause the token splitter to introduce more whitespaces than others.

    parameters:
        sentence -- the full sentence
        cursor_pos -- the current position of the cursor
        token -- current token

    returns: delta between the current position of the cursor and the next occurrence of the given token in that respective sentence
    """
    if token.startswith('##'):
        return 1

    position_of_token = re.search(re.escape(token), sentence[cursor_pos:]).start()
    return position_of_token
