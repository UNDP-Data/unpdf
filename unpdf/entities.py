"""
This module defines common entities used across the package.
"""
# standard library
from typing import Optional

# data management
from pydantic import BaseModel, PrivateAttr


class MetadataEntity(BaseModel):
    length: int
    tokens: list[str]
    noun_chunks: Optional[list[str]]
    subject_phrases: Optional[list[str]]
    dobject_phrases: Optional[list[str]]


class _BaseEntity(BaseModel):
    doc_id: str
    page_id: int
    text: str


class SentenceEntity(_BaseEntity):
    sentence_id: int
    metadata: Optional[MetadataEntity]


class ParagraphEntity(_BaseEntity):
    paragraph_id: int


class PageEntity(_BaseEntity):
    error: bool = False


class DocumentEntity(BaseModel):
    doc_id: str
    pages: list[PageEntity]
    _index: int = PrivateAttr(default=0)

    def __len__(self):
        return len(self.pages)

    def __getitem__(self, index):
        return self.pages[index]

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self.pages):
            page = self.pages[self._index]
            self._index += 1
            return page
        else:
            raise StopIteration

    @property
    def text(self):
        text = ' '.join([page.text for page in self.pages])
        return text
