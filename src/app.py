import os
import dotenv
import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel

from src.api.service import CiRAService, CiRAServiceImpl


description = """The CiRA API wraps the functionality of the Causality in Requirements Artifacts initiative and bundles it in one easy-to-use API.

## Functionality

At the time, the following features are supported:

* **classify** a single, natural language sentence as either causal or non-causal
* **label** each token in a sentence regarding its role within the causal relationship
* generate a cause-effect **graph** from a labeled sentence
* convert a cause-effect graph into a **test suite** containing the minimal number of test cases ensuring full requirements coverage
"""

tags_metadata = [
    {
        "name": "classify",
        "description": "Classification of a single, natural language sentence as either causal or non-causal"
    }, {
        "name": "label",
        "description": "Label each token in a sentence regarding its role within the causal relationship"
    }, {
        "name": "graph",
        "description": "Generate a cause-effect graph from a labeled sentence"
    }, {
        "name": "testsuite",
        "description": "Convert a cause-effect graph into a test suite"
    },
]

app = FastAPI(
    title="Causality in Requirements Artifacts - Pipeline",
    version="1.0.0",
    description=description,
    contact={
        "name": "Julian Frattini",
        "url": "http://www.cira.bth.se/",
        "email": "julian.frattini@bth.se"
    },
    openapi_tags=tags_metadata
)
PREFIX = "/api"

cira: CiRAService = None


def set_cira():
    # determine the location of the pre-trained models
    dotenv.load_dotenv()
    model_env_suffix = '_DEV' if ('DEV_CONTAINER' in os.environ) else ''
    model_classification = os.environ[f'MODEL_CLASSIFICATION{model_env_suffix}']
    model_labeling = os.environ[f'MODEL_LABELING{model_env_suffix}']

    # generate a CiRA service implementation
    cira = CiRAServiceImpl(model_classification, model_labeling)


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


@app.get(PREFIX + '/classify', response_model=ClassificationResponse, tags=['classify'])
async def create_classification(req: SentenceRequest):
    print(cira)
    causal, confidence = cira.classify(req.sentence)
    return ClassificationResponse(causal=causal, confidence=confidence)


@app.get(PREFIX + '/label', response_model=LabelingResponse, tags=['label'])
async def create_labels(req: SentenceRequest):
    labels = cira.sentence_to_labels(sentence=req.sentence)
    return LabelingResponse(labels=labels)


@app.get(PREFIX + '/graph', response_model=GraphResponse, tags=['graph'])
async def create_graph(req: SentenceRequest):
    graph = cira.sentence_to_graph(sentence=req.sentence, labels=req.labels)
    return GraphResponse(graph=graph)


@app.get(PREFIX + '/testsuite', response_model=TestsuiteResponse, tags=['testsuite'])
async def create_testsuite(req: SentenceRequest):
    testsuite = cira.graph_to_test(graph=req.graph, sentence=req.sentence)
    return TestsuiteResponse(suite=testsuite)


if __name__ == '__main__':
    set_cira()
    uvicorn.run(app)
