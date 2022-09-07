import pytest
import os, dotenv
dotenv.load_dotenv()

from src.converters.sentencetolabels.labeler import Labeler
from src.converters.sentencetolabels.labelingconverter import TokenLabel

from src.data.labels import Label

from src.util.loader import load_sentence
from src.util import constants

@pytest.fixture
def sentence(id: str):
    _, sentence, labels, _, _ = load_sentence(filename=f'{constants.SENTENCES_PATH}/sentence{id}.json')
    return {'text': sentence, 'labels': labels}

@pytest.fixture(scope="module")
def labeler():
    return Labeler(model_path=os.environ['MODEL_LABELING'], useGPU=False)

# currently excluded: sentence 10 & 11 (the labeler does not create a negation for "unless"), sentence 13 (there is a tripple-labeling on "NO defect" with Cause3, Variable, and Negation)
@pytest.mark.system
@pytest.mark.parametrize('id', ['1', '1b', '1c', '2', '3', '4', '5', '6', '6b', '7', '8', '12', '14', '16', '17'])
def test_labeler(sentence, labeler):
    """Test that the labeler produces the same labels for a given sentence that a manual annotator would. The manually annotated sentences are stored in .json files and contain both the sentence and the list of manually annotated labels. The test for each sentence is successful if every manual label has exactly one unique equivalent in the list of automatically generated labels. Two labels are equivalent if their (1) name, (2) begin, and (3) end attribute are the same."""
    # abort if the labeler could not be created properly
    assert labeler is not None

    # generate the labels 
    labels_gen = labeler.label(sentence=sentence['text'])
    assert labels_gen is not None

    assert equals(expected=sentence['labels'], generated=labels_gen)

def equals(expected: list[Label], generated: list[Label]) -> bool:
    """Determine whether two list of labels are equal. They count as equal if they have the same length and every label in the expected list has exactly one equivalent in the generated list.
    
    parameters:
        expected -- list of expected labels
        generated -- list of generated labels
        
    returns: True if the two lists are equal"""
    if len(expected) != len(generated):
        return False

    for label in expected:
        equivalent = [candidate for candidate in generated if candidate.begin==label.begin and candidate.name==label.name and candidate.end==label.end]

        if len(equivalent) != 1:
            return False
    
    return True