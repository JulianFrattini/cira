SENTENCES_PATH = './static/sentences'

UNLESS = 'unless'
EXCEPTIVE_CLAUSES = [UNLESS]

# Event
CAUSE = 'Cause'
EFFECT = 'Effect'

def is_event(s):
    return s in (CAUSE, EFFECT)

# Direction
PREDECESSOR = 'predecessor'
SUCCESSOR = 'successor'
TARGET = 'target'
ORIGIN = 'origin'

# Junctor
CONJUNCTION = 'Conjunction'
DISJUNCTION = 'Disjunction'

def is_junctor(s):
    return s in (CONJUNCTION, DISJUNCTION)

# Logic
OR  = 'OR'
AND = 'AND'
POR = 'POR'

# Attribute
VARIABLE = 'Variable'
CONDITION = 'Condition'

NOTRELEVANT = 'notrelevant'

NEGATION = 'Negation'

LABEL_IDS = ['NOT_RELEVANT',
             CAUSE.upper()+'_1', CAUSE.upper()+'_2', CAUSE.upper()+'_3',
             EFFECT.upper()+'_1', EFFECT.upper()+'_2', EFFECT.upper()+'_3',
             AND, OR,
             VARIABLE.upper(), CONDITION.upper(), NEGATION.upper()]

LABEL_IDS_VERBOSE = [NOTRELEVANT,
                     CAUSE+'1', CAUSE+'2', CAUSE+'3',
                     EFFECT+'1', EFFECT+'2', EFFECT+'3',
                     CONJUNCTION, DISJUNCTION,
                     VARIABLE, CONDITION,
                     NEGATION]
