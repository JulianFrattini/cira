import uvicorn
from fastapi import FastAPI, Request
from pydantic import BaseModel
from api.service import CiraServiceMock

app = FastAPI()
PREFIX = "/api"

service = CiraServiceMock(None, None)


class SentenceRequest(BaseModel):
    sentence: str
    language: str = "en"
    labels: list[dict] = []


class ClassificationResponse(BaseModel):
    causal: bool
    confidence: float


@app.get(PREFIX + "/")
def root(req: Request):
    url_list = [
        {"path": route.path, "name": route.name} for route in req.app.routes
    ]
    return url_list


@app.get(PREFIX + "/health")
def health():
    return {"status": "up"}


@app.post(PREFIX + '/classify', response_model=ClassificationResponse)
async def create_classification(req: SentenceRequest):
    causal, confidence = service.classify(req.sentence)
    return ClassificationResponse(causal=causal, confidence=confidence)


if __name__ == '__main__':
    uvicorn.run(app)
