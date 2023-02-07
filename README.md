# Introduction 

`unpdf` is a lightweight utility library for standardised text extraction from PDFs in Python.
It relies on [pypdfium2](https://pypi.org/project/pypdfium2/), an ABI-level Python binding to [PDFium](https://pdfium.googlesource.com/pdfium/+/refs/heads/main), that can boast both high speed and quality of text extraction.
See [benchmarks](https://github.com/py-pdf/benchmarks) comparing `pypdfium2` to other PDF extraction libraries available in Python.

The main goal of this library is to promote a standardised approach to text extraction from PDFs within the organisation.
You can use it in order to:

- Extract a raw text from PDFs documents.
- Split the raw text into paragraph-like structures or sentences.
- Augment sentence-level information with linguistic metadata like named entities.

# Getting Started

You can install the package from GitHub using `pip`:

```bash
# latest version from the default branch (not recommended)
pip install git+https://github.com/undp-data/unpdf.git

# specific version from a tagged release (recommended) 
pip install git+https://github.com/undp-data/unpdf.git@v0.1.0-beta
```

A usage example can be found under `docs/`. Alternatively, you can view the notebook using nbviewer [here](https://github.com/undp-data/unpdf/blob/main/docs/example.ipynb).

Here is a short example:

```python
import unpdf

# extract the text from a PDF
doc = unpdf.extraction.extract_text(file_path='lorem.pdf')

# instantiate a chunker for segmenting the text
chunker = unpdf.chunking.Chunker()

# get the first document page
page = doc.pages[0]  # or somply doc[0] 

# split the first page into sentences
sentences = chunker.get_sentences(page)

# convert the first sentence into a python dictionary
sentence = sentences[0].dict()
```

# Build and Test

TBC. 

# Contribute

The project uses [`poetry`](https://python-poetry.org) for environment management. To replicate the environment locally, you need
to have `poetry` installed on your system. See `poetry` [documentation](https://python-poetry.org/docs/) for details.

All proposed changes or feature enhancements must be implemented in feature branches.
When the changes are finalised, a pull request needs to be submitted.

A typical workflow can be described as follows:

```bash
# fork or clone the project folder
git clone https://github.com/undp-data/unpdf.git

# navigate to the project directory
cd ./unpdf

# install the dependencies
poetry install --with dev

# create a feature branch
git checkout -b <feature branch name>

# now you can make changes or modifications
# don't forget to commit those

# make sure to run tests, if any of those fail, check your code
pytest tests/

# push the feature branch
git push

# finally, create a pull request for your branch to be merged 
```

You can also suggest enhancements or report any problems by creating a New Issue [here](https://github.com/undp-data/unpdf/issues).
