import boto3
from src.models.retrieval_chain import ChatbotRAG
from src.utils.logger import logger
from langchain.globals import set_verbose, set_debug
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose/debug mode."
    )
    parser.add_argument(
        "--embed",
        type=str,
        default="amazon.titan-embed-text-v2:0",
        help="Embedding model.",
    )
    parser.add_argument(
        "--llm", type=str, default="amazon.nova-micro-v1:0", help="LLM model."
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    if args.verbose:
        set_verbose(True)
        set_debug(True)

    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    chatbot = ChatbotRAG(
        client=client, embeddings_id=args.embed, llm_id=args.llm
    )
    chatbot.load_model()
    chatbot.create_chain()
    while True:
        question = input("Enter your question:\n")
        chatbot.query(question=question)
        logger.info(chatbot.res["answer"])
