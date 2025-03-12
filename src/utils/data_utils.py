from langchain_community.document_loaders import PyPDFLoader
from urllib.request import urlretrieve
from src.utils.logger import logger
from pathlib import Path


def get_pdf_from_url(url: str, path: Path):
    doc = None
    try:
        if not url.startswith("http"):
            logger.error(f"Invalid URL: {url}")
            return None
        filename = url.split("/")[-1]
        file_path = path / filename
        if file_path.exists():
            logger.warning(
                f"File {filename} already exists at {file_path}. Skipping download."
            )
        else:
            urlretrieve(url, file_path)
            logger.info(f"Downloaded PDF to {file_path}")
        loader = PyPDFLoader(file_path)
        doc = loader.load()
    except Exception as e:
        logger.error(f"Error loading pdf from url {url}: {e}")
        raise
    return doc
