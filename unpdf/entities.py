"""
This module defines common entities used across the package.
"""
# standard library
from typing import Optional

# data management
from pydantic import BaseModel, PrivateAttr


class _BaseEntity(BaseModel):
    doc_id: str
    page_id: int
    text: str


class Sentence(_BaseEntity):
    sentence_id: int


class QuasiParagraph(_BaseEntity):
    paragraph_id: int


class Page(_BaseEntity):
    error: bool = False


class Document(BaseModel):
    doc_id: str
    pages: list[Page]
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
