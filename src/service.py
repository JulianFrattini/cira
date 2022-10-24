import argparse
from hashlib import sha3_256

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

cira_api = FastAPI()

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
    labels: list[dict] = None

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

@cira_api.post('/api/classify', response_model=ClassificationResponse)
async def create_classification(req: SentenceRequest):
    causal, confidence = cira.classify(sentence=req.sentence)
    return ClassificationResponse(causal=causal, confidence=confidence)

@cira_api.post('/api/label', response_model=LabelsResponse)
async def create_labeling(req: SentenceRequest):
    labels = cira.label(sentence=req.sentence)
    return LabelsResponse(labels=[{"id": label.id, "begin": label.begin, "end": label.end, "name": label.name} for label in labels])

@cira_api.post('/api/graph', response_model=LabelsResponse)
async def create_graph(req: SentenceRequest):
    labels = None
    if req.labels != None:
        labels = req.labels
    else:
        labels = create_labeling(req)
    graph = cira.graph(sentence=req.sentence, labels=labels)
    return None

if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='URL to be used to host the service', type=str, default='127.0.0.1')
    parser.add_argument('--port', help='Port to be used on the localhost for the service', type=int, default=8000)
    args = parser.parse_args()

    # start the service
    uvicorn.run(cira_api, host=args.url, port=args.port)