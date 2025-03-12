import boto3
import uuid
from pathlib import Path
from typing import Optional
from src.utils.logger import logger
from config import DataConfig, ModelConfig, URLS
from langchain.prompts import PromptTemplate
from langchain_aws import ChatBedrockConverse
from langchain_aws.embeddings.bedrock import BedrockEmbeddings
from langchain_chroma import Chroma
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import HumanMessage, AIMessage
from langchain.callbacks.tracers import ConsoleCallbackHandler
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from datetime import datetime
import json


class ChatbotRAG:
    def __init__(
        self,
        client: boto3.client,
        db_path: Path = DataConfig.db_path,
        embeddings_id: str = DataConfig.embedding,
        llm_id: str = ModelConfig.llm_model,
        store: Optional[dict] = None,
    ):
        self.client = client
        self.db_path = db_path
        self.embeddings_id = embeddings_id
        self.llm_id = llm_id
        self.store = store if store else {}
        self.session_id = uuid.uuid4()
        self.rag_chain = None
        self.conv_rag_chain = None

    def load_model(self):
        """Load embedding & LLM model and Chroma database."""
        try:
            self.embeddings_model = BedrockEmbeddings(
                client=self.client, model_id=self.embeddings_id
            )
            self.llm_model = ChatBedrockConverse(
                client=self.client,
                model_id=self.llm_id,
            )
            self.vectordb = Chroma(
                persist_directory=str(self.db_path),
                embedding_function=self.embeddings_model,
            )
        except Exception as e:
            logger.error(f"Error loading models and db: {e}")
            raise

    def create_chain(
        self,
        search_type: str = ModelConfig.search_type,
        k_search: int = ModelConfig.k_search,
    ):
        """Configure history-aware retriever and conversational RAG chain."""
        try:
            self.search_type = search_type
            self.k_search = k_search
            self.retriever = self.vectordb.as_retriever(
                search_type=self.search_type, search_kwargs={"k": self.k_search}
            )

            contextualize_q_prompt = ChatPromptTemplate.from_messages(
                messages=[
                    HumanMessage(content=ModelConfig.contextualize_q_system_prompt),
                    AIMessage(content="Okay."),
                    MessagesPlaceholder(variable_name="chat_history"),
                    ("human", "{input}"),
                ]
            )

            history_aware_retriever = create_history_aware_retriever(
                self.llm_model, self.retriever, contextualize_q_prompt
            )

            qa_prompt = ChatPromptTemplate.from_messages(
                [
                    HumanMessagePromptTemplate(
                        prompt=PromptTemplate(
                            input_variables=["context"],
                            template=ModelConfig.qa_system_prompt,
                        )
                    ),
                    AIMessage(content="Okay."),
                    MessagesPlaceholder("chat_history"),
                    ("human", "{input}"),
                ]
            )

            question_answer_chain = create_stuff_documents_chain(
                self.llm_model, qa_prompt
            )

            self.rag_chain = create_retrieval_chain(
                history_aware_retriever, question_answer_chain
            )

            self.conv_rag_chain = RunnableWithMessageHistory(
                self.rag_chain,
                self.get_session_history,
                input_messages_key="input",
                history_messages_key="chat_history",
                output_messages_key="answer",
            )
        except Exception as e:
            logger.error(f"Error creating retrieval chain: {e}")
            raise

    def get_session_history(self) -> BaseChatMessageHistory:
        """Retrieve or create the session history for the current session."""
        if self.session_id not in self.store:
            self.store[self.session_id] = ChatMessageHistory()
        return self.store[self.session_id]

    def query(self, question: str):
        """Query the chatbot and return the answer."""
        try:
            self.res = self.conv_rag_chain.invoke(
                {"input": question},
                config={
                    "configurable": {"session_id": self.session_id},
                    # "callbacks": [ConsoleCallbackHandler()],
                },
            )
            return self.res["answer"]
        except Exception as e:
            logger.error(f"Error during query: {e}")
            raise


if __name__ == "__main__":
    client = boto3.client("bedrock-runtime", region_name="us-east-1")
    chatbot = ChatbotRAG(client=client)
    chatbot.load_model()
    chatbot.create_chain()
    chatbot.query(question="What are the benefits of filing jointly?")
    chatbot.query(question="How about separately?")
