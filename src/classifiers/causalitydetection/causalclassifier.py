from typing import Tuple

import numpy as np
import torch
import torch.nn.functional as F
from transformers import BertTokenizer

from src.classifiers.causalitydetection.classificationmodel import CausalClassificationModel

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)

CAUSAL = 'causal'
NOT_CAUSAL = 'not causal'
CLASS_NAMES = [NOT_CAUSAL, CAUSAL]
PRE_TRAINED_MODEL_NAME = 'bert-base-cased'
DEVICE_CPU = 'cpu'
DEVICE_GPU = 'cuda:0'
TENSOR_TYPE_PYTORCH = 'pt'

class CausalClassifier:
    def __init__(self, model_path: str):
        """Create a causal detector which wraps the pre-trained classification model.

        parameters:
            path -- path to the binary file of the pre-trained model"""

        self.device = torch.device(DEVICE_GPU if torch.cuda.is_available() else DEVICE_CPU)
        self.tokenizer = BertTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)

        self.model = CausalClassificationModel(len(CLASS_NAMES))
        if torch.cuda.is_available():
            self.model.load_state_dict(torch.load(model_path))
        else:
            self.model.load_state_dict(torch.load(model_path, map_location=DEVICE_CPU))

        self.model = self.model.to(self.device)

    def classify(self, sentence: str) -> Tuple[bool, float]:
        """Classify a natural language sentence regarding whether it is causal or not.

        parameters:
            sentence -- natural language sentence in English

        returns: the classification whether the sentence is causal and the confidence of the classifier"""

        # encode input text
        encoded_text = self.tokenizer.encode_plus(
            sentence,
            max_length=128,
            add_special_tokens=True,
            return_token_type_ids=False,
            padding='max_length',
            return_attention_mask=True,
            return_tensors=TENSOR_TYPE_PYTORCH,
            truncation=True
        )

        # apply classification model
        input_ids = encoded_text['input_ids'].to(self.device)
        attention_mask = encoded_text['attention_mask'].to(self.device)
        output = self.model(input_ids, attention_mask)
        _, prediction = torch.max(output, dim=1)
        probs = F.softmax(output, dim=1)

        # return both the classification and the confidence
        is_causal = (CLASS_NAMES[prediction] == CAUSAL)
        confidence = torch.max(probs, dim=1)[0].item()
        return (is_causal, confidence)

