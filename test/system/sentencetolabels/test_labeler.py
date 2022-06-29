import pytest
import json
import os

from src.converters.sentencetolabels.labeler import Labeler
from src.converters.sentencetolabels.labelingconverter import TokenLabel

SENTENCES_PATH = './test/static/sentences/'
LABEL_IDS_VERBOSE = ['notrelevant', 'Cause1', 'Cause2', 'Cause3', 'Effect1', 'Effect2', 'Effect3', 'Conjunction', 'Disjunction', 'Variable', 'Condition', 'Negation']

@pytest.fixture
def sentence(id: str):
    with open(f'{SENTENCES_PATH}sentence{id}.json', 'r') as f:
        file = json.load(f)
        return {
            'text': file['text'],
            'labels': [label for label in file['labels'] if label['label'] in LABEL_IDS_VERBOSE]
        }

@pytest.fixture(scope="module")
def labeler():
    return Labeler(model_path="C:/Users/juf/Workspace/BTH/NLP_RE/cira/services/bin/multilabel.ckpt", useGPU=True)


# currently excluded: sentence 10 & 11 (the labeler does not create a negation for "unless"), sentence 13 (there is a tripple-labeling on "NO defect" with Cause3, Variable, and Negation)
@pytest.mark.system
@pytest.mark.parametrize('id', ['1', '1b', '1c', '1d', '2', '3', '4', '5', '6', '6b', '7', '8', '12', '14', '16', '17'])
def test_labeler(sentence, labeler):
    """Test that the labeler produces the same labels for a given sentence that a manual annotator would. The manually annotated sentences are stored in .json files and contain both the sentence and the list of manually annotated labels. The test for each sentence is successful if every manual label has exactly one unique equivalent in the list of automatically generated labels. Two labels are equivalent if their (1) name, (2) begin, and (3) end attribute are the same."""
    # abort if the labeler could not be created properly
    assert labeler is not None

    # generate the labels 
    labels_gen = labeler.label(sentence=sentence['text'])
    assert labels_gen is not None
    
    # assert that the number of labels is correct
    assert len(labels_gen) == len(sentence['labels'])

    # generate an equivalence map: map every manual label to its corresponding generated label
    equivalence = {label['id']: None for label in sentence['labels']}
    for label in sentence['labels']:
        # assert, that every manyally annotated label has exactly one equal in the automatically generated labels
        generated_equivalent = [l for l in labels_gen if equal(label, l)]
        assert len(generated_equivalent) == 1
        equivalence[label['id']] = generated_equivalent[0].id
        
    # finally, check that every automatically generated label has only been used for equivalence once
    used_labels_gen = equivalence.keys()
    assert len(used_labels_gen) == len(set(used_labels_gen))

def equal(label_manual, label_generated: TokenLabel) -> bool:
    """True, if the given manually annotated label is equal to the generated label"""

    return label_manual['label'] == label_generated.name and \
        label_manual['begin'] == label_generated.begin and \
            label_manual['end'] == label_generated.end