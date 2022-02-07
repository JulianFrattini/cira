import os.path
import json

import converter.sentencetolabel as s2l
import converter.labelstograph as l2g

def config_labeler(path_to_model):
    # check if the path is valud
    if not os.path.isfile(path_to_model):
        print("Error: the path to the labeling model is not valid.")
        return False
    
    # initialize the labeler with this model
    s2l.use_GPU(False)
    s2l.initialize_model(path_to_model)
    return True

def label_sentence(sentence):
    labels = s2l.label(sentence)
    return labels

if __name__ == "__main__":
    sentence = "If a fire breaks out in the building and no firemen are around, the building needs to be evacuated."

    #config_labeler("C:/Users/juf/Workspace/BTH/NLP_RE/cira/services/bin/multilabel.ckpt")
    #labels = label_sentence(sentence)
    #print(labels)

    labelstring = '[{"id": "T1", "label": "Variable", "begin": 3, "end": 9}, {"id": "T2", "label": "Cause1", "begin": 3, "end": 36}, {"id": "T3", "label": "Condition", "begin": 10, "end": 36}, {"id": "T4", "label": "Conjunction", "begin": 37, "end": 40}, {"id": "T5", "label": "Negation", "begin": 41, "end": 43}, {"id": "T6", "label": "Variable", "begin": 44, "end": 51}, {"id": "T7", "label": "Cause2", "begin": 41, "end": 62}, {"id": "T8", "label": "Condition", "begin": 52, "end": 62}, {"id": "T9", "label": "Variable", "begin": 64, "end": 76}, {"id": "T10", "label": "Effect1", "begin": 64, "end": 98}, {"id": "T11", "label": "Condition", "begin": 77, "end": 98}]'
    labels = json.loads(labelstring)
    l2g.transform(sentence, labels)