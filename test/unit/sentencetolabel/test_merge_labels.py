import pytest

import src.converters.sentencetolabels.labelingconverter as lc
from src.converters.sentencetolabels.labelingconverter import TokenLabel

@pytest.mark.unit
def test_merge1():
    sentence = "If the red button is pressed"
    token_labels = [
        TokenLabel(begin=3, end=6, event=True, name='Cause1'), 
        TokenLabel(begin=3, end=6, event=False, name='Variable'), 
        TokenLabel(begin=7, end=10, event=True, name='Cause1'), 
        TokenLabel(begin=7, end=10, event=False, name='Variable'), 
        TokenLabel(begin=11, end=17, event=True, name='Cause1'), 
        TokenLabel(begin=11, end=17, event=False, name='Variable'), 
        TokenLabel(begin=18, end=20, event=True, name='Cause1'), 
        TokenLabel(begin=18, end=20, event=False, name='Condition'), 
        TokenLabel(begin=21, end=28, event=True, name='Cause1'), 
        TokenLabel(begin=21, end=28, event=False, name='Condition')
    ]
    label_ids_verbose = ['notrelevant', 'Cause1', 'Cause2', 'Cause3', 'Effect1', 'Effect2', 'Effect3', 'Conjunction', 'Disjunction', 'Variable', 'Condition', 'Negation']

    labels = lc.merge_labels(sentence=sentence, token_labels=token_labels, label_ids_verbose=label_ids_verbose)

    cause1 = [label for label in labels if label.name=='Cause1']
    assert len(cause1) == 1
    assert cause1[0].begin == 3
    assert cause1[0].end == 28
    
    variable = [label for label in labels if label.name=='Variable']
    assert len(variable) == 1
    assert variable[0].begin == 3
    assert variable[0].end == 17
    
    condition = [label for label in labels if label.name=='Condition']
    assert len(condition) == 1
    assert condition[0].begin == 18
    assert condition[0].end == 28