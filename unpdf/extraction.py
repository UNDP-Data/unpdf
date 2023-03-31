"""
This module defines routines for extracting text data from PDFs.
"""
# standard library
import os
import logging
from unicodedata import normalize

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


def extract_text(file_path: str, progress_bar: bool = False, **kwargs) -> DocumentEntity:
    """
    Extract text from a .pdf document.

    Parameters
    ----------
    file_path : str
        Path to a pdf to be extracted.
    progress_bar : bool, default=False
        If True, use tqdm as a progress bar when extracting text per page.
    **kwargs
        Any other keyword arguments to be passed on to pdfium.PdfDocument.

    Returns
    -------
    doc : DocumentEntity
        Document entity, containing texts.
    """
    file_name = os.path.basename(file_path)
    file_name, file_extension = os.path.splitext(file_name)
    assert file_extension.lower() == '.pdf', f'Expected a file with .pdf extension, obtained {file_extension}'

    pdf = pdfium.PdfDocument(file_path, **kwargs)
    pages = list()
    iterable = enumerate(pdf)
    for idx, page in tqdm(iterable, disable=not progress_bar):
        try:
            text = page.get_textpage().get_text()
            text, error = _preprocess_text(text), False
        except Exception as e:
            logging.exception(str(e))
            text, error = '', True
        finally:
            page = PageEntity(doc_id=file_name, page_id=idx, text=text, error=error)
            pages.append(page)

    doc = DocumentEntity(doc_id=file_name, pages=pages)
    return doc
