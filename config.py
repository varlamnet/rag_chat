from enum import Enum
from pathlib import Path
from dataclasses import dataclass


class Models(Enum):
    DEEPSEEK_7B = "deepseek-llm-r1-distill-qwen-7b"
    DEEPSEEK_R1 = "deepseek.r1-v1:0"
    TITAN_LITE = "amazon.titan-text-lite-v1"
    TITAN_EXPRESS = "amazon.titan-text-express-v1"
    TITAN_PREMIER = "amazon.titan-text-premier-v1:0"
    TITAN_EMBEDDINGS_V1 = "amazon.titan-embed-text-v1"
    TITAN_EMBEDDINGS_V2 = "amazon.titan-embed-text-v2:0"
    LLAMA_3B = "meta.llama3-2-3b-instruct-v1:0"
    LLAMA_70B = "meta.llama3-3-70b-instruct-v1:0"
    NOVA_MICRO = "amazon.nova-micro-v1:0"


@dataclass(frozen=True)
class DataConfig:
    raw_path: Path = Path(__file__).parent / "data/raw"
    db_path: Path = Path(__file__).parent / "data/vector_db"
    chunk_size: float = 1_000
    chunk_overlap: int = 200
    embedding: str = Models.TITAN_EMBEDDINGS_V2.value


@dataclass(frozen=True)
class ModelConfig:
    llm_model: str = Models.NOVA_MICRO.value
    search_type: str = "similarity"
    k_search: int = 5  # number of relevant searches returned by retriever
    contextualize_q_system_prompt: str = """
        Given a chat history and the latest user question which might \
        reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is.
        """
    qa_system_prompt: str = """
        You are an assistant for answering tax-related questions. Use the following \
        pieces of retrieved context from recent tax documentation to answer \
        the question. When giving the answer, state whether your answer is based \
        on the above documents or not. Try not to exceed five sentences maximum. \

        <context>
        {context}
        </context>
        """


@dataclass(frozen=True)
class WebConfig:
    char_sleep: float = 0.002
    server_port: int = 7860


URLS = [
    "https://www.irs.gov/pub/irs-pdf/i1040gi.pdf",
    "https://www.irs.gov/pub/irs-pdf/p17.pdf",
]
