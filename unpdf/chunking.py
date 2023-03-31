"""
This module defines a Chunker class for chunking entities into paragraphs and sentences.
"""
# standard library
import re
from typing import Union

# text mining
import en_core_web_sm

# utils
from tqdm import tqdm

# local packages
from .entities import SentenceEntity, ParagraphEntity, PageEntity, DocumentEntity
from .mining import get_sentence_metadata


class Chunker:
    def __init__(self, pipe_batch_size: int = 16, add_sentence_metadata: bool = False):
        self.nlp = en_core_web_sm.load(disable=['ner'])
        self.pipe_batch_size = pipe_batch_size
        self.add_sentence_metadata = add_sentence_metadata

    def __repr__(self):
        return f'Chunker(pipe_batch_size={self.pipe_batch_size}, add_sentence_metadata={self.add_sentence_metadata})'

    def __str__(self):
        model_lang = self.nlp.meta['lang']
        model_name = self.nlp.meta['name']
        model_version = self.nlp.meta['version']
        return f'{self.__repr__()} powered by {model_lang} {model_name} model from spaCy v{model_version}.'

    @staticmethod
    def _standardise_spaces(text: str) -> str:
        # replace repeated whitespaces
        text = re.sub(pattern=r'\s+', repl=' ', string=text.strip())
        return text

    def get_quasiparagraphs(self, entity: Union[PageEntity, DocumentEntity]) -> list[ParagraphEntity]:
        """
        Split extracted text into paragraph-like structures.

        This function assumes that a carriage return with a newline character delimit paragraph boundaries if the
        preceding character is a dot, e.g., "This is the end of a paragraph.\r\n". In practice, this seems to work
        reasonably well when coupled with pdfium for extraction.

        Parameters
        ----------
        entity : Union[PageEntity, DocumentEntity]
            Page or document entity to be split into paragraphs.

        Returns
        -------
        paragraphs : list[ParagraphEntity]
            An array of paragraph-like structures.
        """
        if isinstance(entity, DocumentEntity):
            pages = entity.pages
        elif isinstance(entity, PageEntity):
            pages = [entity]
        else:
            raise ValueError('Unsupported entity type.')

        paragraphs = list()
        for page in pages:
            lines, paragraph_id = list(), 0
            for line in re.split(pattern=r'\r\n', string=page.text):
                line = self._standardise_spaces(line)
                lines.append(line)

                # assume it is a paragraph if a line ends with a punctuation mark and there are at least 3 lines already
                if re.search(r'[.!?]$', line) and len(lines) >= 3:
                    paragraph = ParagraphEntity(
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
                paragraph = ParagraphEntity(
                    doc_id=entity.doc_id,
                    page_id=page.page_id,
                    paragraph_id=paragraph_id,
                    text=' '.join(lines),
                )
                paragraphs.append(paragraph)

        return paragraphs

    def get_sentences_from_paragraph(self, paragraph: ParagraphEntity) -> list[SentenceEntity]:
        sentences = list()
        doc = self.nlp(paragraph.text)
        for sentence_id, sent in enumerate(doc.sents):
            sentence = SentenceEntity(
                doc_id=paragraph.doc_id,
                page_id=paragraph.page_id,
                paragraph_id=paragraph.paragraph_id,
                sentence_id=sentence_id,
                text=sent.text,
                metadata=get_sentence_metadata(sent) if self.add_sentence_metadata else None,
            )
            sentences.append(sentence)
        return sentences

    def get_sentences_from_page(self, page: PageEntity) -> list[SentenceEntity]:
        text = self._standardise_spaces(page.text)
        sentences = list()
        for sentence_id, sent in enumerate(self.nlp(text).sents):
            sentence = SentenceEntity(
                doc_id=page.doc_id,
                page_id=page.page_id,
                sentence_id=sentence_id,
                text=sent.text,
                metadata=get_sentence_metadata(sent) if self.add_sentence_metadata else None,
            )
            sentences.append(sentence)
        return sentences

    def get_sentences(
            self,
            entity: Union[ParagraphEntity, PageEntity, DocumentEntity],
            progress_bar: bool = False,
    ) -> list[SentenceEntity]:
        if isinstance(entity, ParagraphEntity):
            sentences = self.get_sentences_from_paragraph(paragraph=entity)
        elif isinstance(entity, PageEntity):
            sentences = self.get_sentences_from_page(page=entity)
        elif isinstance(entity, DocumentEntity):
            sentences = list()
            for page in tqdm(entity.pages) if progress_bar else entity.pages:
                sentences.extend(self.get_sentences_from_page(page))
        else:
            raise ValueError(f'{type(entity)} is not supported. `entity` must be one of (ParagraphEntity, PageEntity, DocumentEntity)')

        return sentences
