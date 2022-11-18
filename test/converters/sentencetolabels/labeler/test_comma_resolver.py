import pytest 
import os, dotenv
dotenv.load_dotenv()

from src.converters.sentencetolabels.labeler import Labeler
from src.data.labels import Label, SubLabel

@pytest.fixture(scope="module")
def labeler() -> Labeler:
    return Labeler(model_path=os.environ['MODEL_LABELING'], useGPU=False)

@pytest.mark.integration
def test_comma(labeler: Labeler):
    sentence = "When deploying, configuring and maintaining the system then the roles must be clear."

    labels = labeler.label(sentence)
    variables: list[SubLabel] = [label for label in labels if label.name=="Variable"]
    
    assert len(variables) == 2

    # make sure each of the two variables has the correct position
    assert variables[0].begin == 44
    assert variables[0].end == 54

    assert variables[1].begin == 60
    assert variables[1].end == 69