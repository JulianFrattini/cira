from converter2.util.labels import Label
from typing import List

class Sentence:
    def __init__(self, text: str, labels: List[Label]):
        self.text = text
        self.labels = labels

    def getLabels(self):
        return self.labels

    def getText(self):
        return self.text

    def __str__(self):
        return self.text