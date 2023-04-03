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
from .cleaning import _normalise_text


def extract_text(
        input_data: Union[str, bytes, BinaryIO, Path],
        doc_id: str = None,
        progress_bar: bool = False,
        **kwargs,
) -> DocumentEntity:
    """
    Extract text from a .pdf document.

    Parameters
    ----------
    input_data : Union[str, bytes, BinaryIO, Path]
        Input data that can be processed by pdfium, e.g., file path, bytes or byte buffer.
    doc_id : str, default=None
        Unique identifier for a document. By default, uses a file name if input_data is a string, otherwise creates
         a unique identifier based on current time.
    progress_bar : bool, default=False
        If True, use tqdm as a progress bar when extracting text per page.
    **kwargs
        Any other keyword arguments to be passed on to pdfium.PdfDocument.

    Returns
    -------
    doc : DocumentEntity
        Document entity, containing texts.
    """
    if doc_id is None and isinstance(input_data, str):
        doc_id = os.path.basename(input_data)  # 'path/to/file.pdf' -> 'file.pdf'
    elif doc_id is None:
        doc_id = f'untitled-v{datetime.utcnow().isoformat()}'

    pdf = pdfium.PdfDocument(input_data, **kwargs)
    pages = list()
    iterable = enumerate(pdf)
    for idx, page in tqdm(iterable, disable=not progress_bar):
        try:
            text = page.get_textpage().get_text_range(index=0, count=-1)  # extract text from the whole page
            text, error = _normalise_text(text), False
        except Exception as e:
            logging.exception(str(e))
            text, error = '', True
        finally:
            page = PageEntity(doc_id=doc_id, page_id=idx, text=text, error=error)
            pages.append(page)

    doc = DocumentEntity(doc_id=doc_id, pages=pages)
    return doc
