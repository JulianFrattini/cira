import pkg_resources

import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

import model_locator
from src.api.service import CiRAService, CiRAServiceImpl

cira_version = pkg_resources.require("cira")[0].version

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
    version=cira_version,
    description=description,
    contact={
        "name": "Julian Frattini",
        "url": "http://www.cira.bth.se/",
        "email": "julian.frattini@bth.se"
    },
    openapi_tags=tags_metadata
)
PREFIX = "/api"

# add CORS middleware allowing all requests from the same localhost
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex='http://localhost:.*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

cira: CiRAService = None


def setup_cira():
    global cira

    model_classification = model_locator.classification()
    model_labeling = model_locator.labeling()
    print(f'Classification model path: {model_classification}')
    print(f'Labeling model path: {model_labeling}')
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
    return {
        "status": "up",
        "cira-version": cira_version
    }


@app.put(PREFIX + '/classify', response_model=ClassificationResponse, tags=['classify'])
async def create_classification(req: SentenceRequest):
    causal, confidence = cira.classify(req.sentence)
    return ClassificationResponse(causal=causal, confidence=confidence)


@app.put(PREFIX + '/label', response_model=LabelingResponse, tags=['label'])
async def create_labels(req: SentenceRequest):
    labels = cira.sentence_to_labels(sentence=req.sentence)
    return LabelingResponse(labels=labels)


@app.put(PREFIX + '/graph', response_model=GraphResponse, tags=['graph'])
async def create_graph(req: SentenceRequest):
    graph = cira.sentence_to_graph(sentence=req.sentence, labels=req.labels)
    return GraphResponse(graph=graph)


@app.put(PREFIX + '/testsuite', response_model=TestsuiteResponse, tags=['testsuite'])
async def create_testsuite(req: SentenceRequest):
    testsuite = cira.graph_to_test(graph=req.graph, sentence=req.sentence)
    return TestsuiteResponse(suite=testsuite)


if __name__ == '__main__':
    setup_cira()
    uvicorn.run(app, host='0.0.0.0')
