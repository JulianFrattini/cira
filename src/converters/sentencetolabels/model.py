import abc

import pytorch_lightning as pl
import torch
from torch import nn
from torch.nn import BCEWithLogitsLoss
from transformers import RobertaModel
from transformers.modeling_outputs import TokenClassifierOutput


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
        self.classifier = nn.Linear(
            self.bert.config.hidden_size, self.num_labels)

    def forward(self, input_ids, attention_mask, token_type_ids, labels):
        outputs = self.bert(
            input_ids=input_ids,
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

                active_labels = labels[attention_mask ==
                                       1].type_as(active_logits)

                loss = loss_fct(active_logits, active_labels)
            else:
                loss = loss_fct(
                    logits.view(-1, self.num_labels), labels.view(-1))

        return TokenClassifierOutput(
            loss=loss,
            logits=logits,
            hidden_states=outputs.hidden_states,
            attentions=outputs.attentions,
        )
