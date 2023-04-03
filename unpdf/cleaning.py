"""
This module defines functions for mining linguistic metadata from sentences.
"""
# standard library
import re
from unicodedata import normalize
from typing import Union

# text mining
from spacy.tokens.span import Span
from spacy.tokens.doc import Doc


def _standardise_spaces(text: str) -> str:
    # replace repeated whitespaces
    text = re.sub(pattern=r'\s+', repl=' ', string=text.strip())
    return text


def _normalise_text(text: str) -> str:
    """
    Preprocess a text by removing unprintable characters and standardising to NFD form.

    The function removes unprintable characters , e.g., '\x02', '\x16' but keeps newline and CR characters.
    NFD normalisation decomposes characters by canonical equivalence, which may be useful for use cases like
    language identification or machine translation.

    Parameters
    ----------
    text : str
        Input text to be cleaned.

    Returns
    -------
    text : str
        NFD-normalised text with unprintable characters removed.
    """
    text = ''.join(char for char in text if char.isprintable() or char in '\r\n')
    text = normalize('NFD', text)  # '\u00E9' or 'é' (b'\xc3\xa9' in NFC) -> 'é' (b'e\xcc\x81' in NFD)
    return text


def simple_preprocess(doc_or_span: Union[Doc, Span], allowed_pos: set[str] = None) -> str:
    """
    Clean a doc or span by removing stopwords and tokens with POS that are not in the allowed list and lemmatising the
    tokens that are left.

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
