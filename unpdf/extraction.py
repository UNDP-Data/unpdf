"""
This module defines routines for extracting text data from PDFs.
"""
# standard library
import os
import logging

# data wrangling
import pypdfium2 as pdfium

# utils
from tqdm import tqdm

# local packages
from .entities import DocumentEntity, PageEntity


def _remove_unprintable(text: str) -> str:
    """
    Remove unprintable characters, e.g., '\x02', '\x16' but keep newline and CR characters.

    Parameters
    ----------
    text : str
        Input text to be cleaned.

    Returns
    -------
    text : str
        Input text with unprintable characters removed.
    """
    text = ''.join(char for char in text if char.isprintable() or char in '\r\n')
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
    for idx, page in tqdm(iterable) if progress_bar else iterable:
        try:
            text = page.get_textpage().get_text()
            text, error = _remove_unprintable(text), False
        except Exception as e:
            logging.exception(str(e))
            text, error = '', True
        finally:
            page = PageEntity(doc_id=file_name, page_id=idx, text=text, error=error)
            pages.append(page)

    doc = DocumentEntity(doc_id=file_name, pages=pages)
    return doc
