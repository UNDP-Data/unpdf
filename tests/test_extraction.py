"""
These are tests for the text extraction module.
"""
# standard library
import os
import re

# local packages
from unpdf.extraction import extract_text
from unpdf.entities import Document


def test_extract_text():
    file_path = os.path.join(__package__, 'lorem.pdf')
    with open(file_path, 'rb') as file:
        contents = file.read()

    for input_data in (file_path, contents):
        doc = extract_text(input_data=input_data)
        # common trigrams with frequency of at least 2
        trigrams = [
            'nec feugiat in', 'Lorem ipsum dolor', 'ipsum dolor sit', 'risus nec feugiat', 'feugiat in fermentum',
            'vitae congue mauris', 'eu augue ut', 'sed euismod nisi', 'euismod nisi porta', 'nisi porta lorem',
            'sapien eget mi', 'odio tempor orci', 'ultricies mi quis', 'mi quis hendrerit', 'quis hendrerit dolor',
            'hendrerit dolor magna.', 'eros in cursus', 'in cursus turpis', 'cursus turpis massa', 'nulla at volutpat',
            'at volutpat diam', 'volutpat diam ut', 'diam ut venenatis.', 'in metus vulputate', 'feugiat in fermentum.',
        ]

        assert isinstance(doc, Document), f'doc must be a DocumentEntity and not {type(doc)}'
        assert isinstance(doc.text, str), f'doc.text must be a string and not {type(doc.text)}'
        assert 6_000 < len(doc.text) < 7_000, f'doc.text length is unexpected {len(doc.text)}'
        text = re.sub(pattern=r'\s+', repl=' ', string=doc.text)
        assert all([text.count(trigram) > 1 for trigram in trigrams]), 'Extracted text is missing expected trigrams.'
