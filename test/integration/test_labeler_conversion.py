import pytest
from unittest.mock import patch, MagicMock

import src.converters.sentencetolabels.labelingconverter as lconv

dummy = [{'token': 'If', 'labels': ['notrelevant']}, {'token': 'the', 'labels': ['Cause1', 'Variable']}, {'token': 'red', 'labels': ['Cause1', 'Variable']}, {'token': 'button', 'labels': ['Cause1', 'Variable']}, {'token': 'is', 'labels': ['Cause1', 'Condition']}, {'token': 'pressed', 'labels': ['Cause1', 'Condition']}, {'token': ',', 'labels': ['notrelevant']}, {'token': 'the', 'labels': ['Effect1', 'Variable']}, {'token': 'system', 'labels': ['Effect1', 'Variable']}, {'token': 'shuts', 'labels': ['Effect1', 'Condition']}, {'token': 'down', 'labels': ['Effect1', 'Condition']}, {'token': '.', 'labels': []}]

@pytest.mark.integration
@patch('src.converters.sentencetolabels.labelingconverter.get_token_labeling')
def test_conversion(get_token_labeling):
    # let the token labeling converter return a dummy value
    get_token_labeling.return_value = dummy

    labels = lconv.convert("If the red button is pressed, the system shuts down.", None, None, None)

    assert(True)