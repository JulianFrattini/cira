import sys
import json
from torch.nn import BCEWithLogitsLoss, MSELoss
from torch import nn
from transformers.modeling_outputs import TokenClassifierOutput
from transformers import RobertaModel
from transformers import RobertaTokenizerFast
from transformers import BatchEncoding

import pytorch_lightning as pl
import torch
from torch.utils.data import Dataset, DataLoader, RandomSampler, SequentialSampler
import torch.nn as nn
import numpy as np
import abc
import transformers
from sklearn.metrics import classification_report

# Dataset configuration variables
LABEL_IDS = ['NOT_RELEVANT', 'CAUSE_1', 'CAUSE_2', 'CAUSE_3', 'EFFECT_1', 'EFFECT_2', 'EFFECT_3', 'AND', 'OR', 'VARIABLE', 'CONDITION', 'NEGATION']
LABEL_IDS_VERBOSE = ['notrelevant', 'Cause1', 'Cause2', 'Cause3', 'Effect1', 'Effect2', 'Effect3', 'Conjunction', 'Disjunction', 'Variable', 'Condition', 'Negation']

MAX_LEN = 80
DROPOUT = 0.13780087432114646

MODEL_PATH = 'bin/multilabel.ckpt'
# set  this variable to false if the machine, on which the python service is supposed to run, is not CUDA-capable
USE_GPU = False

class CustomModel(pl.LightningModule):

    def __init__(self, hyperparams, training_dataset, validation_dataset, test_dataset, labels, model_to_use):
        super().__init__()
        self.hyperparams = hyperparams
        self.training_dataset = training_dataset
        self.validation_dataset = validation_dataset
        self.test_dataset = test_dataset
        self.labels = labels
        self.label2idx = {t: i for i, t in enumerate(labels)}
        self.define_model(model_to_use, len(labels))

        # Variable used to keep track of the best result obtained
        self.best_score = 0
        self.epoch_best_score = 0

    @abc.abstractmethod
    def define_model(self, model_to_use, num_labels):
        raise NotImplementedError

    @abc.abstractmethod
    def forward(self, input_ids, attention_mask, token_type_ids, targets):
        raise NotImplementedError

    @abc.abstractmethod
    def get_predictions_from_logits(self, logits):
        raise NotImplementedError

class MultiLabelRoBERTaCustomModel(CustomModel):

    def get_predictions_from_logits(self, logits):
      sigmoid_outputs = torch.sigmoid(logits)
      predictions = (sigmoid_outputs >= 0.5).int()

      return predictions

    def define_model(self, model_to_use, num_labels):
        self.num_labels = num_labels
        self.bert = RobertaModel.from_pretrained(model_to_use)    
        self.dropout = nn.Dropout(self.hyperparams["dropout"])
        self.classifier = nn.Linear(self.bert.config.hidden_size, self.num_labels)

    def forward(self, input_ids, attention_mask, token_type_ids, labels):
      outputs = self.bert(
              input_ids = input_ids,
              attention_mask=attention_mask
          )

      sequence_output = outputs[0]

      sequence_output = self.dropout(sequence_output)
      logits = self.classifier(sequence_output)

      loss = None
      if labels is not None:
        loss_fct = BCEWithLogitsLoss()
        # Only keep active parts of the loss
        if attention_mask is not None:
            active_logits = logits[attention_mask == 1]
            
            active_labels = labels[attention_mask == 1].type_as(active_logits)

            loss = loss_fct(active_logits, active_labels)
        else:
            loss = loss_fct(logits.view(-1, self.num_labels), labels.view(-1))

      return TokenClassifierOutput(
          loss=loss,
          logits=logits,
          hidden_states=outputs.hidden_states,
          attentions=outputs.attentions,
      )

TOKENIZER = None
model = None

def initialize_model(MODEL_PATH):
    global TOKENIZER, model

    ##############Paramaters related to the BERT model type###################
    MODEL_TO_USE = 'roberta-base'
    TOKENIZER = RobertaTokenizerFast.from_pretrained(MODEL_TO_USE)
    MODEL_CLASS = MultiLabelRoBERTaCustomModel
    ###########################################################################


    MODEL_PARAMS = {'dropout': DROPOUT}

    model = MODEL_CLASS.load_from_checkpoint(hyperparams=MODEL_PARAMS,
                                            training_dataset=None,
                                            validation_dataset=None,
                                            test_dataset=None,
                                            labels=LABEL_IDS,
                                            model_to_use=MODEL_TO_USE,
                                            checkpoint_path=MODEL_PATH)

    if USE_GPU:
        model.cuda()

    model.eval()


def label(sentence):
    tokenized_batch: BatchEncoding = TOKENIZER(text=[sentence],
                                               add_special_tokens=True,
                                               max_length=MAX_LEN,
                                               truncation=True,
                                               padding='max_length'
                                               )

    input_ids = torch.tensor(tokenized_batch.input_ids, dtype=torch.long)
    attention_mask = torch.tensor(
        tokenized_batch.attention_mask, dtype=torch.long)

    if USE_GPU:
        input_ids = input_ids.cuda()
        attention_mask = attention_mask.cuda()

    outputs = model(input_ids,
                    attention_mask,
                    token_type_ids=None,
                    labels=None
                    )

    logits = outputs.logits
    sigmoid_outputs = torch.sigmoid(logits)
    predictions = (sigmoid_outputs >= 0.5).int()
    predictions = predictions.cpu()

    # bring labels into processable form
    labels = []
    
    tokenindex = 0
    charindex_begincurrenttoken = 0
    charindex_endlasttoken = 0
    labelindex = 1

    currentCauseLabel = ''
    currentCauseBeginIndex = -1
    causelabelswitched = False

    currentVariableLabel = ''
    currentVariableBeginIndex = -1

    # iterate over all tokens within the sentence
    sentence_tokens = tokenized_batch[0].tokens
    for token_prediction_idx, token_prediction in enumerate(predictions[0]):
        # get the current token
        token = sentence_tokens[token_prediction_idx]
        token = token.replace("Ġ", "")
        if token == '</s>' or token == '<pad>' or token == '<sep>':
            break

        # get all labels associated with the token
        token_predicted_labels = []
        for label_prediction_idx, label_prediction in enumerate(token_prediction):
            if label_prediction == 1:
                token_predicted_labels.append(LABEL_IDS_VERBOSE[label_prediction_idx])
        #print(f'{token} - {token_predicted_labels}')

        # cause labels
        if len(token_predicted_labels) > 0:
            label_cause = token_predicted_labels[0]
        else:
            label_cause = ''

        if currentCauseLabel != '' and currentCauseLabel != label_cause:
            causelabelswitched = True
            # create the label
            labels.append({'id': 'T'+str(labelindex), 'label': currentCauseLabel, 'begin': currentCauseBeginIndex, 'end': charindex_endlasttoken})
            labelindex = labelindex+1
            currentCauseLabel = ""
            currentCauseBeginIndex = -1
        if currentCauseLabel == '' and label_cause != 'notrelevant':
            # begin a new label
            currentCauseLabel = label_cause
            currentCauseBeginIndex = charindex_begincurrenttoken

        # variable labels
        if len(token_predicted_labels) > 1:
            label_variable = token_predicted_labels[1]
        else:
            label_variable = ''
        if currentVariableLabel != '':
            if currentVariableLabel != label_variable:
                # create the label
                labels.append({'id': 'T'+str(labelindex), 'label': currentVariableLabel, 'begin': currentVariableBeginIndex, 'end': charindex_endlasttoken})
                labelindex = labelindex+1
                currentVariableLabel = ""
                currentVariableBeginIndex = -1
            elif currentVariableLabel == label_variable and causelabelswitched:
                labels.append({'id': 'T'+str(labelindex), 'label': currentVariableLabel, 'begin': currentVariableBeginIndex, 'end': charindex_endlasttoken})
                labelindex = labelindex+1
                currentVariableBeginIndex = charindex_begincurrenttoken
        if currentVariableLabel == '' and  label_variable != 'notrelevant':
            # begin a new label
            currentVariableLabel = label_variable
            currentVariableBeginIndex = charindex_begincurrenttoken

        # reset the causelabelswitched flag
        causelabelswitched = False

        tokenindex = tokenindex+1

        if token == '<sep>' or token == '<pad>':
            break
        elif token != '<s>':
            charindex_endlasttoken = charindex_begincurrenttoken + len(token)
            charindex_begincurrenttoken = get_new_begin_char_index(charindex_begincurrenttoken, sentence, token)

    return labels

# TODO catch all corner cases in the char index increase
def increase_char_index(token):
    if token.startswith('##'):
        return 1
    elif token == ',':
        return len(token)
    elif token.startswith("'"):
        return len(token)
    else:
        return len(token) + 1

# calculates the new char index, when adding the token to the current char index
def get_new_begin_char_index(currentCharIndex, sentence, token):
    newCharIndex = currentCharIndex + len(token)
    if len(sentence) > newCharIndex:
        currentChar = sentence[newCharIndex]
        # increment the new char index until the current char is not an empty space anymore (should not take more than one increment)
        while currentChar == " ":
            newCharIndex+=1
            currentChar = sentence[newCharIndex]
    
    return newCharIndex
