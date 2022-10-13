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
    id: str
    sentence: str
    labels: list[dict]

@cira_api.get('/api')
def read_api_version():
    return {'version': 'v1'}

# returns the number of existing labeled sentences from the cache
@cira_api.get('/api/labels')
def get_labels():
    return {'number_of_labels': len(cira_api.cache)}

# delete the cache
@cira_api.delete('/api/cache')
def delete_classification():
    cira_api.cache = {}

    
if __name__ == '__main__':
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='URL to be used to host the service', type=str, default='127.0.0.1')
    parser.add_argument('--port', help='Port to be used on the localhost for the service', type=int, default=8000)
    args = parser.parse_args()

    # start the service
    uvicorn.run(cira_api, host=args.url, port=args.port)