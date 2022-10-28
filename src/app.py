import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel

from src.api.service import CiRAService, CiRAServiceImpl

import os, dotenv
dotenv.load_dotenv()

model_env_suffix = '_DEV' if ('DEV_CONTAINER' in os.environ) else ''

model_classification = os.environ[f'MODEL_CLASSIFICATION{model_env_suffix}']
model_labeling = os.environ[f'MODEL_LABELING{model_env_suffix}']

app = FastAPI()
PREFIX = "/api"

service: CiRAService = CiRAServiceImpl(model_classification=model_classification, model_labeling=model_labeling)


class SentenceRequest(BaseModel):
    sentence: str
    language: str = "en"
    labels: list[dict] = []
    graph: dict = None


class ClassificationResponse(BaseModel):
    causal: bool
    confidence: float

class LabelingResponse(BaseModel):
    labels: list[dict]

class GraphResponse(BaseModel):
    graph: dict

class TestsuiteResponse(BaseModel):
    suite: dict


@app.get(PREFIX + "/")
def root(req: Request):
    url_list = [
        {"path": route.path, "name": route.name} for route in req.app.routes
    ]
    return url_list


@app.get(PREFIX + "/health")
def health():
    return {"status": "up"}


@app.get(PREFIX + '/classify', response_model=ClassificationResponse)
async def create_classification(req: SentenceRequest):
    causal, confidence = service.classify(req.sentence)
    return ClassificationResponse(causal=causal, confidence=confidence)


@app.get(PREFIX + '/label', response_model=LabelingResponse)
async def create_labels(req: SentenceRequest):
    labels = service.sentence_to_labels(sentence=req.sentence)
    return LabelingResponse(labels=labels)


@app.get(PREFIX + '/graph', response_model=GraphResponse)
async def create_graph(req: SentenceRequest):
    graph = service.sentence_to_graph(sentence=req.sentence, labels=req.labels)
    return GraphResponse(graph=graph)


@app.get(PREFIX + '/testsuite', response_model=TestsuiteResponse)
async def create_classification(req: SentenceRequest):
    testsuite = service.graph_to_test(graph=req.graph)
    return TestsuiteResponse(suite=testsuite)


if __name__ == '__main__':
    uvicorn.run(app)
