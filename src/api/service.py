
class CiraServiceMock:
    model_classification = None
    model_labeling = None

    def __init__(self, model_classification, model_labeling):
        self.model_classification = model_classification
        self.model_labeling = model_labeling
    def classify(self, sentence):
        return True, 42.0
