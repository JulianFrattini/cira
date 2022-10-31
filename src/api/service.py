from abc import abstractmethod

from src.cira import CiRAConverter

from src.data.labels import Label
from src.data.labels import from_dict as labels_from_dict

from src.data.graph import Graph
from src.data.graph import from_dict as graph_from_dict

from src.data.test import Suite


class CiRAService:
    @abstractmethod
    def classify(self, sentence: str) -> tuple[bool, float]:
        pass

    @abstractmethod
    def sentence_to_labels(self, sentence: str) -> list[dict]:
        pass

    @abstractmethod
    def sentence_to_graph(self, sentence: str, labels: list) -> dict:
        pass

    @abstractmethod
    def graph_to_test(self, graph) -> dict:
        pass


class CiRAServiceImpl(CiRAService):

    def __init__(self, model_classification: str, model_labeling: str, use_GPU: bool = False):
        self.cira = CiRAConverter(
            classifier_causal_model_path=model_classification,
            converter_s2l_model_path=model_labeling,
            use_GPU=use_GPU)

    def classify(self, sentence: str) -> tuple[bool, float]:
        """Classify a given sentence as either causal or non-causal.

        parameters:
            sentence -- single natural language sentence

        returns:
            causal -- True, if the sentence is considered to be causal
            confidence -- float value between 0 and 1 representing the confidence with which the classified chose either label"""
        causal, confidence = self.cira.classify(sentence)
        return causal, confidence

    def sentence_to_labels(self, sentence: str) -> list[dict]:
        """Generate the causal labels for a sentence.

        parameters:
            sentence -- single natural language sentence

        returns: list of labels serialized to dictionaries
        """
        labels: list[Label] = self.cira.label(sentence)

        # serialize all labels and return them
        serialized = [label.to_dict() for label in labels]
        return serialized

    def sentence_to_graph(self, sentence: str, labels: list) -> dict:
        """Generate a cause-effect-graph from a sentence and a list of labels. If the labels are not given, they will be generated.

        parameters:
            sentence -- single natural language sentence
            labels -- list of labels (either as true labels or dictionaries)

        returns: graph serialized to a dictionary
        """
        # recover the list of labels if necessary
        labels: list[Label] = self.recover_labels(sentence, labels)

        # generate the graph
        graph = self.cira.graph(sentence, labels)

        # serialize the graph and return it
        serialized = graph.to_dict()
        return serialized

    def recover_labels(self, sentence: str, labels: list) -> list[Label]:
        """Recovers a list of labels and ensures that it is in the right format. This includes (1) generating new labels if the current list is None or empty and (2) casting labels serialized to dictionaries back to actual labels.
        
        parameters:
            sentence -- single, causal, natural language sentence
            labels -- list of labels
            
        returns: list of actual labels representing the causal relationship implied by the sentence"""
        # if the labels are not provided, generate them
        if labels is None or len(labels) == 0:
            return self.cira.label(sentence)

        # if the labels are serialized, deserialize them
        if type(labels[0]) == dict:
            return labels_from_dict(labels)

        # otherwise, the labels are already recovered
        return labels


    def graph_to_test(self, graph) -> dict:
        """Generate a test suite from a cause-effect graph.

        parameters:
            graph -- a cause effect graph (either as a true Graph or a dictionary)

        returns: test suite serialized to a dictionary
        """
        # deserialize the graph in case it is not
        if type(graph) == dict:
            graph = graph_from_dict(graph)

        suite: Suite = self.cira.testsuite(ceg=graph)

        # serialize the test suite and return it
        serialized = suite.to_dict()
        return serialized


class CiraServiceMock(CiRAService):
    model_classification = None
    model_labeling = None

    def __init__(self, model_classification, model_labeling):
        self.model_classification = model_classification
        self.model_labeling = model_labeling

    def classify(self, sentence) -> tuple[bool, float]:
        return True, 0.99


    def sentence_to_labels(self, sentence: str) -> list[dict]:
        return [{'id': 'L1', 'name': 'Variable', 'begin': 10, 'end': 20, 'parent': None}]


    def sentence_to_graph(self, sentence: str, labels: list) -> dict:
        return {
            'nodes': [
                {'id': 'c', 'variable': 'the button', 'condition': 'is pressed'},
                {'id': 'e', 'variable': 'the system', 'condition': 'shuts down'}
                ],
            'root': 'c',
            'edges': [{'origin': 'c', 'target': 'e', 'negated': False}]
        }


    def graph_to_test(self, graph) -> dict:
        return {
            'conditions': [{'id': 'c', 'variable': 'the button', 'condition': 'is pressed'}],
            'expected': [{'id': 'c', 'variable': 'the system', 'condition': 'shuts down'}],
            'cases': [{'c': True, 'e': True}, {'c': False, 'e': False}]
        }