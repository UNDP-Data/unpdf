"""
This module defines functions for mining linguistic metadata from sentences.
"""
# standard library
from typing import Union

# text mining
from spacy.tokens.span import Span
from spacy.tokens.doc import Doc
from spacy.symbols import nsubj

# local packages
from .entities import MetadataEntity


def get_subject_phrases(doc_or_span: Union[Doc, Span]):
    phrases = list()
    for token in doc_or_span:
        if token.dep == nsubj:
            subtree = list(token.subtree)
            start, end = subtree[0].i, subtree[-1].i + 1
            phrase = doc_or_span[start:end].text
            if phrase:
                phrases.append(phrase)
    return phrases


def get_sentence_metadata(sent: Span, keep_stopwords: bool = False) -> MetadataEntity:
    sentence_metadata = MetadataEntity(
        length=len(sent),
        tokens=[token.text for token in sent if not token.is_stop or keep_stopwords],
        noun_chunks=[noun_chunk.text for noun_chunk in sent.noun_chunks] or None,
        subject_phrases=get_subject_phrases(doc_or_span=sent) or None,
    )
    return sentence_metadata
