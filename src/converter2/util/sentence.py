class Sentence:
    def __init__(self, t: str, lab):
        self.text = t
        self.labels = lab

    def get_labels(self):
        return self.labels

    def getText(self):
        return self.text

    def __str__(self):
        return self.text