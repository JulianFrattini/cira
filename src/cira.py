import os.path
import json

#from converter.util.sentence import Sentence
#import converter.sentencetolabel as s2l
#import converter.labelstograph as l2g

import converter2.labelstograph as labelstograph
from converter2.util.sentence import Sentence
from converter2.util.labels import fromJson
from converter2.util.event import Event, EventList

#def config_labeler(path_to_model):
#    # check if the path is valud
#    if not os.path.isfile(path_to_model):
#        print("Error: the path to the labeling model is not valid.")
#        return False
    
    # initialize the labeler with this model
#    s2l.use_GPU(False)
#    s2l.initialize_model(path_to_model)
#    return True

#def label_sentence(sentence):
#    labels = s2l.label(sentence)
#    return labels

if __name__ == "__main__":
    text = "If a fire breaks out in the building and either no firemen are around or the people start to panic, the building needs to be evacuated."

    #config_labeler("C:/Users/juf/Workspace/BTH/NLP_RE/cira/services/bin/multilabel.ckpt")
    #labels = label_sentence(sentence)
    #print(labels)

    #labels = [{"id": "T1", "label": "Variable", "begin": 3, "end": 9}, {"id": "T2", "label": "Cause1", "begin": 3, "end": 36}, {"id": "T3", "label": "Condition", "begin": 10, "end": 36}, {"id": "T4", "label": "Conjunction", "begin": 37, "end": 40}, {"id": "T5", "label": "Negation", "begin": 48, "end": 50}, {"id": "T6", "label": "Variable", "begin": 51, "end": 58}, {"id": "T7", "label": "Cause2", "begin": 48, "end": 69}, {"id": "T8", "label": "Condition", "begin": 59, "end": 69}, {"id": "T9", "label": "Disjunction", "begin": 70, "end": 72}, {"id": "T10", "label": "Variable", "begin": 73, "end": 83}, {"id": "T11", "label": "Cause3", "begin": 73, "end": 98}, {"id": "T12", "label": "Condition", "begin": 84, "end": 98}, {"id": "T13", "label": "Variable", "begin": 100, "end": 112}, {"id": "T14", "label": "Effect1", "begin": 100, "end": 134}, {"id": "T15", "label": "Condition", "begin": 113, "end": 134}]
    #sentence = Sentence(sentence, labels)

    #labelstograph.transform(sentence)


    labels = [{"id": "T1", "label": "Variable", "begin": 3, "end": 9}, {"id": "T2", "label": "Cause1", "begin": 3, "end": 36}, {"id": "T3", "label": "Condition", "begin": 10, "end": 36}, {"id": "T4", "label": "Conjunction", "begin": 37, "end": 40}, {"id": "T5", "label": "Negation", "begin": 48, "end": 50}, {"id": "T6", "label": "Variable", "begin": 51, "end": 58}, {"id": "T7", "label": "Cause2", "begin": 48, "end": 69}, {"id": "T8", "label": "Condition", "begin": 59, "end": 69}, {"id": "T9", "label": "Disjunction", "begin": 70, "end": 72}, {"id": "T10", "label": "Variable", "begin": 73, "end": 83}, {"id": "T11", "label": "Cause3", "begin": 73, "end": 98}, {"id": "T12", "label": "Condition", "begin": 84, "end": 98}, {"id": "T13", "label": "Variable", "begin": 100, "end": 112}, {"id": "T14", "label": "Effect1", "begin": 100, "end": 134}, {"id": "T15", "label": "Condition", "begin": 113, "end": 134}]

    labellist = fromJson(labels)
    sentence = Sentence(text, labellist)    
    
    graph = labelstograph.transform(sentence)
