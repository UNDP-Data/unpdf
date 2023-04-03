"""
This module defines a Chunker class for chunking entities into paragraphs and sentences.
"""
# standard library
import re
from typing import Union, Callable

# text mining
import en_core_web_sm

# utils
from tqdm import tqdm

# local packages
from .entities import Sentence, QuasiParagraph, Page, Document
from .cleaning import _standardise_spaces


class Chunker:
    def __init__(self, preprocess_sent_func: Callable = None):
        self.nlp = en_core_web_sm.load(disable=['ner'])
        self.preprocess_sent_func = preprocess_sent_func

    def __repr__(self):
        return 'Chunker()'

    def __str__(self):
        model_lang = self.nlp.meta['lang']
        model_name = self.nlp.meta['name']
        model_version = self.nlp.meta['version']
        return f'{self.__repr__()} powered by {model_lang} {model_name} model from spaCy v{model_version}.'

    def get_quasiparagraphs(self, entity: Union[Page, Document]) -> list[QuasiParagraph]:
        """
        Split extracted text into paragraph-like structures.

        This function assumes that a carriage return with a newline character delimit paragraph boundaries if the
        preceding character is a dot, e.g., "This is the end of a paragraph.\r\n". In practice, this seems to work
        reasonably well when coupled with pdfium for extraction.

        Parameters
        ----------
        entity : Union[Page, Document]
            Page or document entity to be split into paragraphs.

        Returns
        -------
        paragraphs : list[QuasiParagraphEntity]
            An array of paragraph-like structures.
        """
        if isinstance(entity, Document):
            pages = entity.pages
        elif isinstance(entity, Page):
            pages = [entity]
        else:
            raise ValueError('Unsupported entity type.')

        paragraphs = list()
        for page in pages:
            lines, paragraph_id = list(), 0
            for line in re.split(pattern=r'\r\n', string=page.text):
                line = _standardise_spaces(line)
                lines.append(line)

                # assume it is a paragraph if a line ends with a punctuation mark and there are at least 3 lines already
                if re.search(r'[.!?]$', line) and len(lines) >= 3:
                    paragraph = QuasiParagraph(
                        doc_id=entity.doc_id,
                        page_id=page.page_id,
                        paragraph_id=paragraph_id,
                        text=' '.join(lines),
                    )
                    paragraphs.append(paragraph)
                    paragraph_id += 1
                    lines.clear()

            # handle the remaining lines if needed
            if lines:
                paragraph = QuasiParagraph(
                    doc_id=entity.doc_id,
                    page_id=page.page_id,
                    paragraph_id=paragraph_id,
                    text=' '.join(lines),
                )
                paragraphs.append(paragraph)

        return paragraphs

    def get_sentences_from_paragraph(self, paragraph: QuasiParagraph) -> list[Sentence]:
        sentences = list()
        doc = self.nlp(paragraph.text)
        for sent_id, sent in enumerate(doc.sents):
            sentence = Sentence(
                doc_id=paragraph.doc_id,
                page_id=paragraph.page_id,
                paragraph_id=paragraph.paragraph_id,
                sentence_id=sent_id,
                text=sent.text if self.preprocess_sent_func is None else self.preprocess_sent_func(sent),
            )
            sentences.append(sentence)
        return sentences

    def get_sentences_from_page(self, page: Page) -> list[Sentence]:
        text = _standardise_spaces(page.text)
        sentences = list()
        for sent_id, sent in enumerate(self.nlp(text).sents):
            sentence = Sentence(
                doc_id=page.doc_id,
                page_id=page.page_id,
                sentence_id=sent_id,
                text=sent.text if self.preprocess_sent_func is None else self.preprocess_sent_func(sent),
            )
            sentences.append(sentence)
        return sentences

    def get_sentences(self, entity: Union[QuasiParagraph, Page, Document], progress_bar: bool = False) -> list[Sentence]:
        if isinstance(entity, QuasiParagraph):
            sentences = self.get_sentences_from_paragraph(paragraph=entity)
        elif isinstance(entity, Page):
            sentences = self.get_sentences_from_page(page=entity)
        elif isinstance(entity, Document):
            sentences = list()
            for page in tqdm(entity.pages) if progress_bar else entity.pages:
                sentences.extend(self.get_sentences_from_page(page))
        else:
            raise ValueError(f'{type(entity)} is not supported. `entity` must be one of (QuasiParagraph, Page, Document)')

        return sentences
