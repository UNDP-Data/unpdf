"""
These are tests for the linguistic features mining module.
"""
# text mining
import en_core_web_sm

# local packages
from unpdf.mining import get_phrases


def test_get_phrases():
    nlp = en_core_web_sm.load(disable=['ner'])
    sentence2phrases = {
        'This is a sentence.': {'This'},
        'What sentence is this?': {'this'},
        'A short sentence is fine but longer sentences are even better.': {'A short sentence', 'longer sentences'},
        'Colorless green ideas sleep furiously.': {'Colorless green ideas'},
        'The limits of my language mean the limits of my world.': {'The limits of my language'},
    }
    for sentence, phrases_expected in sentence2phrases.items():
        doc = nlp(sentence)
        phrases_actual = set(get_phrases(doc_or_span=doc, dep='nsubj'))
        assert phrases_expected == phrases_actual, f'Expected {phrases_expected} but got {phrases_actual}'
