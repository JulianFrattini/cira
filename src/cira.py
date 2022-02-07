import os.path

import converter.sentencetolabel as s2l

def config_labeler(path_to_model):
    if not os.path.isfile(path_to_model):
        print("Error: the path to the labeling model is not valid.")
        return False
    
    s2l.initialize_model(path_to_model)
    return True

if __name__ == "__main__":
    sentence = "If a fire breaks out in the building and no firemen are around, the building needs to be evacuated."
    config_labeler('C:/Users/juf/Workspace/BTH/NLP_RE/cira/services/bin/multilabel.ckpt')
    labels = s2l.label(sentence)
    print(labels)
