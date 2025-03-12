import boto3
import time
import gradio as gr
from src.models.retrieval_chain import ChatbotRAG
from src.utils.logger import logger
from config import WebConfig
from gradio import ChatMessage
from random import random


def query_llm(message, history):
    global chatbot

    if not history:
        logger.debug("Instantiating Chatbot.")
        chatbot = ChatbotRAG(
            client=boto3.client("bedrock-runtime", region_name="us-east-1"),
        )
        chatbot.load_model()
        chatbot.create_chain()

    start_time = time.time()
    response = ChatMessage(
        content="",
        metadata={"title": "_Thinking_ step-by-step", "id": 0, "status": "pending"},
    )
    yield response

    # not really tho
    thoughts = [
        "Thinking ...",
        "Thinking harder ... 🤔",
        "Thinking even harder ... 🤔🤔🤔",
    ]

    accumulated_thoughts = ""
    for thought in thoughts:
        time.sleep(random())
        accumulated_thoughts += f"- {thought}\n\n"
        response.content = accumulated_thoughts.strip()
        yield response

    response.metadata["status"] = "done"
    response.metadata["duration"] = time.time() - start_time
    yield response

    res = chatbot.query(message)
    tmp = ""
    for char in res:
        tmp += char
        time.sleep(WebConfig.char_sleep)
        yield [response, ChatMessage(content=tmp)]


app = gr.ChatInterface(
    query_llm,
    title="RAG Chatbot for Tax Questions 🚀",
    description="""
        <center>
            📣 Ask question about taxes!
            <br>
            ️<i> For informational purposes only, not tax advice. </i>
        </center>
        """,
    type="messages",
    flagging_mode="manual",
    flagging_options=["Like", "Spam", "Inappropriate", "Other"],
    save_history=True,
    theme=gr.themes.Ocean(
        text_size="lg",
        spacing_size="sm",
        radius_size="lg",
    ),
    examples=[
        ["What documents do I need to file my taxes?"],
        ["What are the benefits of filing married jointly?"],
        ["I filed the taxes, when will I get my refund?"],
    ],
)

if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=WebConfig.server_port,
        debug=False,
        share=False,
    )
