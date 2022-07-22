
from typing import Tuple

# classifiers
from src.classifiers.causalitydetection.causalclassifier import CausalClassifier

# converters
from src.converters.sentencetolabels.labeler import Labeler
from src.converters.labelstograph.graphconverter import GraphConverter
from src.converters.labelstograph.eventresolver import SimpleResolver
from src.converters.graphtotestsuite.testsuiteconverter import convert as convert_graph_to_testsuite

from src.data.labels import Label
from src.data.graph import Graph
from src.data.test import Suite

class CiRAConverter():

    def __init__(self, classifier_causal_model_path: str, converter_s2l_model_path: str, use_GPU: bool=False):
        # initialize classifiers
        self.classifier_causal = CausalClassifier(model_path=classifier_causal_model_path)

        # initialize converters
        self.converter_sentencetolabel = Labeler(model_path=converter_s2l_model_path, useGPU=use_GPU)
        self.converter_labeltograph = GraphConverter(eventresolver=SimpleResolver())

    def classify(self, sentence: str) -> Tuple[bool, float]:
        causal, confidence = self.classifier_causal.classify(sentence)
        return (causal, confidence)

    def process(self, sentence: str) -> Tuple[list[Label], Graph, Suite]:
        labels: list[Label] = self.converter_sentencetolabel.label(sentence)
        graph: Graph = self.converter_labeltograph.generate_graph(sentence, labels)
        suite: Suite = convert_graph_to_testsuite(graph)

        return (labels, graph, suite)