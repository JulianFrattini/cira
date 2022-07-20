import pytest
import os, dotenv
dotenv.load_dotenv()

from src.classifiers.causalitydetection.causalclassifier import CausalClassifier

@pytest.fixture(scope="module")
def sut() -> CausalClassifier:
    return CausalClassifier(path=os.environ['MODEL_CLASSIFICATION'])

@pytest.mark.system
@pytest.mark.parametrize('sentence, causal', [
    ('If the red button is pushed the system shuts down.', True),
    ('The architecture of the system utilizes a broker pattern.', False)
])
def test_classifier(sut: CausalClassifier, sentence, causal):
    classification, confidence = sut.classify(sentence=sentence)
    assert classification == causal