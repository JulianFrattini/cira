from src.converters.sentencetolabels.model import MultiLabelRoBERTaCustomModel
from transformers import RobertaTokenizerFast
from transformers import BatchEncoding
import torch

from typing import List
from src.data.labels import Label
import src.converters.sentencetolabels.labelingconverter as lconv

# Dataset configuration variables
LABEL_IDS = ['NOT_RELEVANT', 'CAUSE_1', 'CAUSE_2', 'CAUSE_3', 'EFFECT_1', 'EFFECT_2', 'EFFECT_3', 'AND', 'OR', 'VARIABLE', 'CONDITION', 'NEGATION']
LABEL_IDS_VERBOSE = ['notrelevant', 'Cause1', 'Cause2', 'Cause3', 'Effect1', 'Effect2', 'Effect3', 'Conjunction', 'Disjunction', 'Variable', 'Condition', 'Negation']


class Labeler:

    def __init__(self, model_path: str='bin/multilabel.ckpt', useGPU: bool=False, max_len: int=80, dropout: float=0.13780087432114646):
        # set variables
        self.model_path = model_path
        self.useGPU = useGPU
        self.max_len = max_len
        self.dropout = dropout

        # setup model and tokenizer
        MODEL_TO_USE = 'roberta-base'
        self.tokenizer = RobertaTokenizerFast.from_pretrained(MODEL_TO_USE)
        self.model = MultiLabelRoBERTaCustomModel.load_from_checkpoint(hyperparams={'dropout': self.dropout}, 
            training_dataset=None, 
            validation_dataset=None, 
            test_dataset=None,
            labels=LABEL_IDS, 
            model_to_use=MODEL_TO_USE, 
            checkpoint_path=self.model_path
        )

        if self.useGPU:
            self.model.cuda()

        self.model.eval()

    def use_GPU(self, use: bool) -> None:
        """Set the flag of whether the machine learning algorithm is supposed to use the GPU or not

        parameters:
            use: bool -- true, if a CUDA-capable GPU is available and shall be used
        """
        self.useGPU = use

    def label(self, sentence: str) -> List[Label]: 
        # tokenize the sentence
        tokenized_batch: BatchEncoding = self.tokenizer(
            text=[sentence], 
            add_special_tokens=True, 
            max_length=self.max_len, 
            truncation=True, 
            padding='max_length' )

        # attention mask
        input_ids = torch.tensor(tokenized_batch.input_ids, dtype=torch.long)
        attention_mask = torch.tensor(tokenized_batch.attention_mask, dtype=torch.long)

        # utilize CUDA if possible
        if self.use_GPU:
            input_ids = input_ids.cuda()
            attention_mask = attention_mask.cuda()

        # generate outputs
        outputs = self.model(input_ids, attention_mask, token_type_ids=None, labels=None )

        # generate prediction
        logits = outputs.logits
        sigmoid_outputs = torch.sigmoid(logits)
        predictions = (sigmoid_outputs >= 0.5).int()
        predictions = predictions.cpu()

        # return list of labels
        labels: List[Label] = lconv.convert(
            sentence=sentence,
            sentence_tokens=tokenized_batch[0].tokens, 
            predictions=predictions, 
            label_ids_verbose=LABEL_IDS_VERBOSE)
        return labels