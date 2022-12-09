import os
import dotenv
import pytest


from fastapi.testclient import TestClient
from fastapi import status

import app
from src.api.service import CiRAServiceImpl

sentence = "If the button is pressed then the system shuts down."
API_URL = 'http://localhost:8000/api/'

labels: list[dict] = [
    {'id': 'L0', 'name': 'Cause1', 'begin': 3, 'end': 24, 'successor': {
        'id': 'L1', 'junctor': None}, 'children': ['L2', 'L4']},
    {'id': 'L1', 'name': 'Effect1', 'begin': 30, 'end': 51,
        'successor': None, 'children': ['L3', 'L5']},
    {'id': 'L2', 'name': 'Variable', 'begin': 3, 'end': 13, 'parent': 'L0'},
    {'id': 'L3', 'name': 'Variable', 'begin': 30, 'end': 40, 'parent': 'L1'},
    {'id': 'L4', 'name': 'Condition', 'begin': 14, 'end': 24, 'parent': 'L0'},
    {'id': 'L5', 'name': 'Condition', 'begin': 41, 'end': 51, 'parent': 'L1'},
]

graph = {
    'nodes': [{'id': 'E0', 'variable': 'the button', 'condition': 'is pressed'}, {'id': 'E1', 'variable': 'the system', 'condition': 'shuts down'}],
    'root': 'E0',
    'edges': [{'origin': 'E0', 'target': 'E1', 'negated': False}]
}

suite = {
    'conditions': [{'id': 'P0', 'variable': 'the button',
                    'condition': 'is pressed'}],
    'expected': [{'id': 'P1', 'variable': 'the system',
                  'condition': 'shuts down'}],
    'cases': [{'P0': True, 'P1': True}, {'P0': False, 'P1': False}]
}


@pytest.fixture(scope="module")
def client() -> TestClient:
    # determine the location of the classification and labeling model
    dotenv.load_dotenv()
    model_env_suffix = '_DEV' if ('DEV_CONTAINER' in os.environ) else ''
    model_classification = os.environ[f'MODEL_CLASSIFICATION{model_env_suffix}']
    model_labeling = os.environ[f'MODEL_LABELING{model_env_suffix}']

    # create the system under test
    app.cira = CiRAServiceImpl(
        model_classification=model_classification, model_labeling=model_labeling)

    client = TestClient(app.app)
    return client


@pytest.mark.system
def test_classification(client):
    response = client.post(
        f'{API_URL}classify', json={"sentence": sentence})

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body['causal'] == True
    assert body['confidence'] > 0.9


@pytest.mark.system
def test_classification_empty_sentence(client):
    response = client.post(
        f'{API_URL}classify', json={"sentence": ""})

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body['causal'] == False
    assert body['confidence'] > 0.9


@pytest.mark.system
def test_classification_missing_sentence(client):
    response = client.post(
        f'{API_URL}classify', json={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.system
def test_classification_missing_sentence_recovery(client):
    response = client.post(
        f'{API_URL}classify', json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # assert that after a failed request a valid request will succeed
    response = client.post(
        f'{API_URL}classify', json={"sentence": sentence})
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.system
def test_labeling(client):
    response = client.post(
        f'{API_URL}label', json={"sentence": sentence})

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body['labels'] == labels


@pytest.mark.system
def test_labeling_emtpy_sentence(client):
    response = client.post(
        f'{API_URL}label', json={"sentence": ""})

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body['labels'] == []


@pytest.mark.system
def test_graph(client):
    response = client.post(
        f'{API_URL}graph', json={"sentence": sentence})

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body['graph'] == graph


@pytest.mark.system
def test_suite(client):
    response = client.post(
        f'{API_URL}testsuite', json={"sentence": sentence, "graph": graph})

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body['suite'] == suite


@pytest.mark.system
def test_suite_missing_graph(client):
    response = client.post(
        f'{API_URL}testsuite', json={"sentence": sentence})

    assert response.status_code == status.HTTP_200_OK

    body = response.json()
    assert body['suite'] == suite
