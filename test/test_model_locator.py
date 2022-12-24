import pytest
import model_locator


@pytest.mark.unit
def test_locate_labeling_model():
    model_path = model_locator.LABELING
    assert model_path.endswith('.ckpt')


@pytest.mark.unit
def test_locate_classification_model():
    model_path = model_locator.CLASSIFICATION
    assert model_path.endswith('.bin')


@pytest.mark.unit
def test_locate_labeling_model_in_container(mocker):
    mocker.patch("os.path.isfile", return_value=True)

    model_path = model_locator.__load_model_env('MODEL_CONTAINER_DEV')
    assert model_path == 'container/cira-labeler.ckpt'


@pytest.mark.unit
def test_locate_classification_model_in_container(mocker):
    mocker.patch("os.path.isfile", return_value=False)

    with pytest.raises(NameError):
        model_locator.__load_model_env('MODEL_CONTAINER_DEV')


@pytest.mark.unit
def test_locate_unkown_env():
    with pytest.raises(NameError):
        model_locator.__load_model_env('NOT_EXISTING_ENV')
