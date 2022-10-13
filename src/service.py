import argparse
from hashlib import sha3_256

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

cira_api = FastAPI()
cira_api.cache = dict()

import os, dotenv
dotenv.load_dotenv()
model_env_suffix = '_DEV' if ('DEV_CONTAINER' in os.environ) else ''
model_classification = os.environ[f'MODEL_CLASSIFICATION{model_env_suffix}']
model_labeling = os.environ[f'MODEL_LABELING{model_env_suffix}']

from src.cira import CiRAConverter
cira = CiRAConverter(classifier_causal_model_path=model_classification, converter_s2l_model_path=model_labeling)

class SentenceRequest(BaseModel):
    sentence: str
    language: str = "en"

class ClassificationResponse(BaseModel):
    causal: bool
    confidence: float

class LabelsResponse(BaseModel):
    labels: list[dict]

class GraphResponse(BaseModel):
    labels: list[dict]

# heartbeat
@cira_api.get('/api')
def read_api_version():
    return {'version': 'v1'}

# cache management
@cira_api.get('/api/cache')
def get_cache():
    return cira_api.cache

@cira_api.delete('/api/cache')
def delete_classification():
    cira_api.cache = {}


def access_cache(sentence: str) -> dict:
    req_id = sha3_256(sentence.encode('utf-8')).hexdigest()
    if not req_id in cira_api.cache:
        cira_api.cache[req_id] = {
            "sentence": sentence
        }
    return cira_api.cache[req_id]

@cira_api.post('/api/classify', response_model=ClassificationResponse)
async def create_classification(req: SentenceRequest):
    cache = access_cache(req.sentence)
    if "classification" not in cache.keys():
        causal, confidence = cira.classify(sentence=req.sentence)
        cache['classification'] = ClassificationResponse(causal=causal, confidence=confidence)
    return cache['classification']

@cira_api.post('/api/label', response_model=LabelsResponse)
async def create_labeling(req: SentenceRequest):
    cache = access_cache(req.sentence)
    if "labels" not in cache.keys():
        labels = cira.label(sentence=req.sentence)
        cache['labels'] = LabelsResponse(labels=[{"id": label.id, "begin": label.begin, "end": label.end, "name": label.name} for label in labels])
    return cache['labels']

if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='URL to be used to host the service', type=str, default='127.0.0.1')
    parser.add_argument('--port', help='Port to be used on the localhost for the service', type=int, default=8000)
    args = parser.parse_args()

    # start the service
    uvicorn.run(cira_api, host=args.url, port=args.port)