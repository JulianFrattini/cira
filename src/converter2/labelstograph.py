from converter2.util.sentence import Sentence

def transform(sentence: Sentence):
    # build skeleton of the graph
    # get all causal nodes (assume that they appear next to each other with no effect node in the middle)

    # get all junctors between each adjacent pair of cause nodes

    # resolve the junctors following precedence rules: either > and > or

    # resolve additional negations

    # add effect nodes to the graph

    # resolve each causal node, i.e., "fill" each node with its values

    return None