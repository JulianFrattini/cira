
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

    def __init__(self, classifier_causal_model_path: str, converter_s2l_model_path: str, use_GPU: bool = False):
        """Create a converter that exhibits the CiRA functionality (classification, labeling, CEG generation, test case generation).

        parameters:
            classifier_causal_model_path -- path to the pre-trained classification model (https://zenodo.org/record/5159501#.Ytq28ITP3-g)
            converter_s2l_model_path -- path to the pre-trained labeling model (https://zenodo.org/record/5550387#.Ytq3QYTP3-g) (use the model named roberta_dropout_linear_layer_multilabel.ckpt for optimal performance)
            use_GPU -- True if the executing system can offer CUDA to accelerate the usage of the language models
        """
        # initialize classifiers
        self.classifier_causal = CausalClassifier(model_path=classifier_causal_model_path)

        # initialize converters
        self.converter_sentencetolabel = Labeler(model_path=converter_s2l_model_path, useGPU=use_GPU)
        self.converter_labeltograph = GraphConverter(eventresolver=SimpleResolver())

    def classify(self, sentence: str) -> Tuple[bool, float]:
        """Classify a natural language sentence regarding whether it is causal or not.

        parameters:
            sentence -- natural language sentence in English

        returns: the classification whether the sentence is causal and the confidence of the classifier"""
        causal, confidence = self.classifier_causal.classify(sentence)
        return (causal, confidence)

    def label(self, sentence: str) -> list[Label]:
        """Label each token contained in a causal, natural language sentence with its respective role in the causal relationship.

        parameters:
            sentence -- natural language sentence in English

        returns: A list of labels
        """
        labels: list[Label] = self.converter_sentencetolabel.label(sentence)
        return labels

    def graph(self, sentence: str, labels: list[Label]) -> Graph:
        """Convert a sentence and a list of labels to a cause-effect graph

        parameters:
            sentence -- natural language sentence in English
            labels -- list of labels representing the role of each token in the sentence in respect to the causal relationship

        returns: a cause-effect graph
        """
        graph: Graph = self.converter_labeltograph.generate_graph(sentence, labels)
        return graph

    def testsuite(self, ceg: Graph) -> Suite:
        """Convert a cause-effect graph into a test suite containing the minimal set of test cases necessary to assert that the requirement is met.

        parameters:
            ceg -- cause-effect graph

        returns: a minimal test suite.
        """
        suite: Suite = convert_graph_to_testsuite(ceg)
        return suite

    def process(self, sentence: str) -> Tuple[list[Label], Graph, Suite]:
        """Process a causal, natural language sentence and generate (a) a list of labels, (b) a cause-effect graph, and (c) a minimal test suite from it.

        parameters:
            sentence -- natural language sentence in English

        returns: Tuple containing (a) a list of labels, (b) a cause-effect graph, and (c) a minimal test suite.
        """
        labels: list[Label] = self.converter_sentencetolabel.label(sentence)
        graph: Graph = self.converter_labeltograph.generate_graph(sentence, labels)
        suite: Suite = convert_graph_to_testsuite(graph)

        return (labels, graph, suite)

