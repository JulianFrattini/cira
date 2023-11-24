import torch
from transformers import BertModel


class CausalClassificationModel(torch.nn.Module):
    def __init__(self, n_classes: int, pre_trained_model_name: str='bert-base-cased'):
        super(CausalClassificationModel, self).__init__()
        self.bert = BertModel.from_pretrained(pre_trained_model_name)
        self.drop = torch.nn.Dropout(p=0.3)
        self.out = torch.nn.Linear(self.bert.config.hidden_size, n_classes)

    def forward(self, input_ids, attention_mask):
        _, pooled_output = self.bert(input_ids=input_ids, attention_mask=attention_mask, return_dict=False)
        output = self.drop(pooled_output)
        return self.out(output)

