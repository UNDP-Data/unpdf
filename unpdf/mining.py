"""
This module defines functions for mining linguistic metadata from sentences.
"""
# standard library
from typing import Union

# text mining
from spacy.tokens.span import Span
from spacy.tokens.doc import Doc


def preprocess_sent(doc_or_span: Union[Doc, Span], allowed_pos: set[str] = None) -> str:
    """
    Clean a doc by removing stopwords and tokens with POS that are not in the allowed list and lemmatising the tokens
    that are left.

    For reference on POS tagging scheme, see https://spacy.io/usage/linguistic-features#pos-tagging.

    Parameters
    ----------
    doc_or_span : Union[Doc, Span]
        A spaCy Doc or Span object to be cleaned.
    allowed_pos : set[str], default=None
        A set of POS tags to be included. If not provided, only 'NOUN', 'VERB', 'ADJ' are kept.

    Returns
    -------
    text : str
        A cleaned concatenated text of lemmatised tokens.
    """
    allowed_pos = allowed_pos or {'NOUN', 'VERB', 'ADJ'}
    tokens = [token.lemma_ for token in doc_or_span if token.pos_ in allowed_pos and not token.is_stop]
    text = ' '.join(tokens)
    return text
