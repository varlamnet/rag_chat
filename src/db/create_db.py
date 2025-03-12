import boto3
from typing import List
from src.utils.data_utils import get_pdf_from_url
from src.utils.logger import logger
from config import DataConfig, URLS
from langchain_chroma import Chroma
from langchain_aws.embeddings.bedrock import BedrockEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def fetch_documents(urls: List[str]) -> List:
    """Fetch PDFs from the list of URLs and return all documents."""
    documents = []
    for url in urls:
        try:
            logger.info(f"Fetching document from {url}")
            doc = get_pdf_from_url(url, DataConfig.raw_path)
            if doc:
                documents.extend(doc)
            else:
                logger.warning(f"No documents retrieved from {url}")
        except Exception as e:
            logger.error(f"Error fetching document from {url}: {e}")
    return documents


def split_documents(
    documents: List,
    chunk_size: int = DataConfig.chunk_size,
    chunk_overlap: int = DataConfig.chunk_overlap,
) -> List:
    """Split documents into smaller chunks."""
    if chunk_size <= chunk_overlap:
        logger.warning("Chunk size must be greater than chunk overlap!")
    if not documents:
        logger.warning("No documents to split.")

    logger.info(
        f"Splitting documents into chunks with size {chunk_size} and overlap {chunk_overlap}"
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return text_splitter.split_documents(documents)


def get_vectordb_from_splits(splits: List, client: boto3.client) -> Chroma:
    """Create and persist the vector database."""
    logger.info("Creating vector database")
    try:
        embeddings_model = BedrockEmbeddings(
            client=client, model_id=DataConfig.embedding
        )
        vectordb = Chroma.from_documents(
            persist_directory=str(DataConfig.db_path),
            documents=splits,
            embedding=embeddings_model,
        )
        logger.info("Vector database created and persisted successfully")
    except Exception as e:
        logger.error(f"Error creating or persisting vector database: {e}")
        raise
    return vectordb


def create_vectordb(
    urls: List[str],
    client: boto3.client,
    chunk_size: int = DataConfig.chunk_size,
    chunk_overlap: int = DataConfig.chunk_overlap,
) -> None:
    """Main function to create a vector database from a list of URLs."""
    try:
        documents = fetch_documents(urls)
        splits = split_documents(documents, chunk_size, chunk_overlap)
        get_vectordb_from_splits(splits, client)

    except Exception as e:
        logger.error(f"Error creating vector database: {e}")
        raise


if __name__ == "__main__":
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    create_vectordb(URLS, client, chunk_size=1_000, chunk_overlap=200)
