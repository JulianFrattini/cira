import pytest
import model_locator


@pytest.mark.unit
def test_locate_labeling_model():
    model_path = model_locator.labeling()
    assert model_path.endswith('cira-labeler.ckpt')


@pytest.mark.unit
def test_locate_classification_model():
    model_path = model_locator.classification()
    assert model_path.endswith('cira-classifier.bin')

