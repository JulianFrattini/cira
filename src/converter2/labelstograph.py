from converter2.util.sentence import Sentence
from converter2.util.labels import Label, mapCausalLabels, conjunctionsBetween

def transform(sentence: Sentence):
    # build skeleton of the graph
    # get all causal nodes (assume that they appear next to each other with no effect node in the middle)
    labels = sentence.getLabels()
    causes = mapCausalLabels(labels, justCauses=True)
    causenames = list(causes.keys())

    # get all junctors between each adjacent pair of cause nodes
    if len(causes) > 1:
        for one, two in zip(causenames[:-1], causenames[1:]):
            first = causes[one]
            second = causes[two]

            conjunctions = conjunctionsBetween(first, second, labels)


    # resolve the junctors following precedence rules: either > and > or

    # resolve additional negations

    # add effect nodes to the graph

    # resolve each causal node, i.e., "fill" each node with its values

    return None