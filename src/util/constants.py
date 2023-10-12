from enum import Enum, EnumMeta

SENTENCES_PATH = './static/sentences'

LABEL_IDS = ['NOT_RELEVANT', 'CAUSE_1', 'CAUSE_2', 'CAUSE_3', 'EFFECT_1', 'EFFECT_2', 'EFFECT_3', 'AND', 'OR', 'VARIABLE', 'CONDITION', 'NEGATION']
LABEL_IDS_VERBOSE = ['notrelevant', 'Cause1', 'Cause2', 'Cause3', 'Effect1', 'Effect2', 'Effect3', 'Conjunction', 'Disjunction', 'Variable', 'Condition', 'Negation']

# Event
CAUSE = 'Cause'
EFFECT = 'Effect'
is_event = lambda s: s == CAUSE or s == EFFECT

# Direction
PREDECESSOR = 'predecessor'
SUCCESSOR = 'successor'

# Junctor
CONJUNCTION = 'Conjunction'
DISJUNCTION = 'Disjunction'
is_junctor = lambda s: s == CONJUNCTION or s == DISJUNCTION

# Logic
OR  = 'OR'
AND = 'AND'
POR = 'POR'

NOTRELEVANT = 'notrelevant'
