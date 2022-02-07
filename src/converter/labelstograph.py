
def transform(sentence, labels):
    # get all causal labels
    print(get_labels_of_type(labels, 'Cause'))

    # generate a CEG node for each label

    # generate the edges between the nodes

def get_labels_of_type(labels, type: str):
    relevant_labels = []
    for label in labels:
        if label['label'].startswith(type):
            relevant_labels.append(label)
    return relevant_labels