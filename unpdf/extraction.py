"""
This module defines routines for extracting text data from PDFs.
"""
# standard library
import os
import logging
from unicodedata import normalize
from datetime import datetime
from pathlib import Path
from typing import Union, BinaryIO

# data wrangling
import pypdfium2 as pdfium

# utils
from tqdm import tqdm

# local packages
from .entities import DocumentEntity, PageEntity


def _preprocess_text(text: str) -> str:
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


def extract_text(input_data: Union[str, bytes, BinaryIO, Path], progress_bar: bool = False, **kwargs) -> DocumentEntity:
    """
    Extract text from a .pdf document.

    Parameters
    ----------
    input_data : Union[str, bytes, BinaryIO, Path]
        Input data that can be processed by pdfium, e.g., file path, bytes or byte buffer.
    progress_bar : bool, default=False
        If True, use tqdm as a progress bar when extracting text per page.
    **kwargs
        Any other keyword arguments to be passed on to pdfium.PdfDocument.

    Returns
    -------
    doc : DocumentEntity
        Document entity, containing texts.
    """
    if isinstance(input_data, str):
        doc_id = os.path.basename(input_data)  # 'path/to/file.pdf' -> 'file.pdf'
    else:
        doc_id = f'untitled-v{datetime.utcnow().isoformat()}'

    pdf = pdfium.PdfDocument(input_data, **kwargs)
    pages = list()
    iterable = enumerate(pdf)
    for idx, page in tqdm(iterable, disable=not progress_bar):
        try:
            text = page.get_textpage().get_text_range(index=0, count=-1)
            text, error = _preprocess_text(text), False
        except Exception as e:
            logging.exception(str(e))
            text, error = '', True
        finally:
            page = PageEntity(doc_id=doc_id, page_id=idx, text=text, error=error)
            pages.append(page)

    doc = DocumentEntity(doc_id=doc_id, pages=pages)
    return doc
