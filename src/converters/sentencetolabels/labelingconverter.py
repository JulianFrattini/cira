from functools import reduce
import functools
from typing import List
from xmlrpc.client import Boolean
from src.data.labels import Label
from dataclasses import dataclass

@dataclass
class TokenLabel:
    begin: int
    end: int
    event: bool
    name: str

def convert(sentence: str, sentence_tokens, predictions, label_ids_verbose: List[str]) -> List[Label]: 
    """Convert the list of sentence tokens and the list of predictions into a list of label objects"""
    labels: List[Label] = []

    token_labels = get_token_labeling(sentence_tokens=sentence_tokens, predictions=predictions, label_ids_verbose=label_ids_verbose)
    
    labels = merge_labels(sentence=sentence, token_labels=token_labels, label_ids_verbose=label_ids_verbose)

    return labels

def get_token_labeling(sentence_tokens, predictions, label_ids_verbose: List[str]) -> List[TokenLabel]:
    """Convert the list of sentence tokens, predictions, and label ids into a list of tokens associated to all available labels
    
    parameters: 
        sentence_tokens -- list of sentence tokens (usually one token per word or special character)
        predictions -- list of predictions for each token, associating each available label with a weight within [0;1]
        label_ids_verbose -- ordered list of labels corresponding to the predictions
    
    returns:
        token_labels -- list of TokenLabels, containing one object for each token label (max 2 per token)
    """
    token_labels = []
    cursor = 0

    for token_prediction_idx, token_prediction in enumerate(predictions[0]):
        # get the current token
        token: str = sentence_tokens[token_prediction_idx]
        token = token.replace("Ġ", "")

        # skip the initializing token
        if token == '<s>':
            continue
        # stop once a finalizing token is reached
        if token in ['</s>', '<pad>', '<sep>']:
            break

        # get all labels associated to a token
        for label_prediction_idx, label_prediction in enumerate(token_prediction):
            if label_prediction == 1:
                #token_predicted_labels.append(label_ids_verbose[label_prediction_idx]) 
                label = label_ids_verbose[label_prediction_idx]
                if label != 'notrelevant':
                    token_labels.append(TokenLabel(
                        begin=cursor, 
                        end=cursor+len(token), 
                        event = 'Cause' in label or 'Effect' in label, 
                        name=label))

        # advance the cursor to the position of the next token in the sentence
        cursor += advance_cursor(token)
        
    return token_labels

def merge_labels(sentence: str, token_labels: List[TokenLabel], label_ids_verbose: List[str]) -> List[Label]:
    """Convert the list of token labels, where every single token is associated to up to two labels, to a list of merged labels, where each label spans all tokens that belong to the same label.

    parameters:
        sentence -- the literal sentence
        token_labels -- list of each token within the sentence associated to up to two labels

    returns:
        list of merged labels 
    """
    merged_labels: List[Label] = []
    id_counter = 0
    # keep track of event borders (begin and end of an event label)
    event_borders = []

    for ltype in label_ids_verbose:
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
            merged_labels.append(Label(id=idv, name=l.name, begin=l.begin, end=l.end))
            if l.name[:-1] in ['Cause', 'Effect']:
                event_borders.extend([l.begin, l.end])
            id_counter += 1

    return merged_labels

def advance_cursor(token: str) -> int:
    """Calculate the amount of characters the cursor needs to jump to the next token. The calculation takes into account that certain characters cause the token splitter to introduce more whitespaces than others.

    parameters:
        token -- current token

    returns:
        number of characters until the next token
    """
    if token.startswith('##'):
        return 1
    elif token == ',':
        return len(token)
    elif token.startswith("'"):
        return len(token)
    else:
        return len(token) + 1