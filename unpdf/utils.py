"""
This module contains utilities for downloading and manipulating external PDFs
"""
# standard library
import os
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

# web services
import requests

# utils
from tqdm import tqdm


def extract_file_name(url: str, repair: bool = False) -> str:
    """
    Extract file name part of a URL.

    Parameters
    ----------
    url : str
        URL to a file.
    repair : bool, default=False
        If True, repair an invalid value to always return a valid file name.
    Returns
    -------
    file_name : str
        File name extracted from the URL.

    Examples
    --------
    >>> extract_file_name('http://some.website.com/file.pdf')
    'file.pdf'
    >>> extract_file_name('http://some.website.com/path/subpath/subsubpath/file.pdf')
    'file.pdf'
    >>> extract_file_name('http://some.website.com/file')
    'file'
    >>> extract_file_name('http://some.website.com/file/')
    ''
    """
    path = urlparse(url).path
    file_name = os.path.basename(path.strip('/'))

    if repair:
        if not file_name:
            file_name = 'new_file.pdf'
        elif not file_name.endswith('.pdf'):
            file_name = f'{file_name}.pdf'

    return file_name


def download_pdf(url: str, save_dir: str = None, chunk_size: int = 2048) -> bool:
    """
    Download a binary object to a local drive.

    Parameters
    ----------
    url : str
        URL to a binary object.
    save_dir : str, default=None
        Directory to save the PDF to. If None, resolves to the current working directory.
    chunk_size : int, default=2048
        Size of chunks in bytes.

    Returns
    -------
    True if the file was downloaded, False if the response code was not 200.
    """
    if save_dir is None:
        save_dir = os.curdir

    response = requests.get(url, timeout=10, stream=True)
    if response.status_code != 200:
        return False
    file_name = extract_file_name(url=url, repair=True)
    file_path = os.path.join(save_dir, file_name)
    with open(file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            file.write(chunk)
    return True


def download_pdfs(urls: list[str], save_dir: str = None,  max_workers: int = 4) -> dict[bool, int]:
    """
    Speed up PDF download using multithreading.

    Parameters
    ----------
    urls : list[str]
        List of URLs to PDF files.
    save_dir : str, default=None
        Directory to save the PDF to. If None, resolves to the current working directory.
    max_workers : int, default=4
        Number of workers to use.

    Returns
    -------
    stats : dict[bool, int]
        Stats dict with True counts for downloads and False counts for errors.
    """
    stats = {True: 0, False: 0}
    futures = list()

    with tqdm(total=len(urls)) as pbar:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            for url in urls:
                future = pool.submit(download_pdf, url=url, save_dir=save_dir)
                future.add_done_callback(lambda x: pbar.update())
                futures.append(future)

            for future in as_completed(futures):
                result = future.result()
                stats[result] += 1
    return stats
