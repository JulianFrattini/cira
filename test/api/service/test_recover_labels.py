import pytest
import unittest.mock as mock
from unittest.mock import patch

from src.api.service import CiRAServiceImpl
from src.data.labels import SubLabel

sentence = "If the button is pressed than the system shuts down."


@pytest.fixture(scope="module")
@patch('src.api.service.CiRAConverter', autospec=True)
def isolatedService(converter) -> CiRAServiceImpl:
    mockedConverter = mock.MagicMock()
    mockedConverter.label.return_value = [SubLabel(id='L1', name='Variable', begin=3, end=14)]
    converter.return_value = mockedConverter

    service = CiRAServiceImpl(model_classification=None, model_labeling=None)
    return service


@pytest.mark.unit
def test_recover_none(isolatedService):
    labels = isolatedService.get_deserialized_labels(sentence, labels=None)
    expected = [SubLabel(id='L1', name='Variable', begin=3, end=14)]
    assert labels == expected


@pytest.mark.unit
def test_recover_empty(isolatedService):
    labels = isolatedService.get_deserialized_labels(sentence, labels=[])
    expected = [SubLabel(id='L1', name='Variable', begin=3, end=14)]
    assert labels == expected


@pytest.mark.unit
def test_recover_serialized(isolatedService):
    labels = isolatedService.get_deserialized_labels(sentence, labels=[{'id': 'L1', 'name': 'Variable', 'begin': 3, 'end': 14, 'parent': None}])
    expected = [SubLabel(id='L1', name='Variable', begin=3, end=14)]
    assert labels == expected


@pytest.mark.unit
def test_recover_existing(isolatedService):
    labels = isolatedService.get_deserialized_labels(sentence, labels=[SubLabel(id='L1', name='Variable', begin=3, end=14)])
    expected = [SubLabel(id='L1', name='Variable', begin=3, end=14)]
    assert labels == expected

