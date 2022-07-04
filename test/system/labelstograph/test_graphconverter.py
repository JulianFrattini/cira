import pytest, json

from src.converters.labelstograph.graphconverter import GraphConverter
from src.converters.labelstograph.eventresolver import SimpleResolver

from src.converters.sentencetolabels.labelingconverter import connect_labels

from src.data.labels import Label, EventLabel, SubLabel

SENTENCES_PATH = './test/static/sentences/'
LABELS_EVENT = ['Cause1', 'Cause2', 'Cause3', 'Effect1', 'Effect2', 'Effect3']
LABELS_SUB = ['Conjunction', 'Disjunction', 'Variable', 'Condition', 'Negation']

@pytest.fixture
def sut() -> GraphConverter:
    return GraphConverter(eventresolver=SimpleResolver())

@pytest.fixture
def sentence(id: str):
    with open(f'{SENTENCES_PATH}sentence{id}.json', 'r') as f:
        file = json.load(f)

        # extract all relevant labels
        labels: list[Label] = []
        for label in file['labels']:
            if label['label'] in LABELS_EVENT:
                labels.append(EventLabel(id=label['id'], name=label['label'], begin=label['begin'], end=label['end']))
            elif label['label'] in LABELS_SUB:
                labels.append(SubLabel(id=label['id'], name=label['label'], begin=label['begin'], end=label['end']))
        connect_labels(labels)

        return {
            'text': file['text'],
            'labels': labels
        }

@pytest.mark.parametrize('id', ['7'])
def test_1(sentence, sut: GraphConverter):
    print(sentence)
    graph = sut.generate_graph(sentence['text'], sentence['labels'])
    assert str(graph) == '([an error].(is present) || ([the debugger].(is active) && [an exception].(is triggered))) ===> [a log entry].(will be created)'
