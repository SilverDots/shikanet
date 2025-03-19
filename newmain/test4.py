import json
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
import json

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

from evaluation.eval import Evaluator
from data_loader.loader import ChatDB, discord_loader, krishna_loader

llm = ChatOpenAI(model="gpt-4o")

from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI
from data_loader.loader import discord_loader
import logging

# db = discord_loader()
# vectordb = db.vector_store
llm = ChatOpenAI(temperature=0)
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import ChatOpenAI

from data_loader.loader import discord_loader, krishna_loader

# db = discord_loader()
db = krishna_loader()

import logging

# Set up the logger
logging.basicConfig(level=logging.INFO)

vectorstore = db.vector_store

metadata_field_info = [
    AttributeInfo(
        name="datetime_int",
        description="""
        The time the message was sent. Integer representation of the datetime using
        self.data["datetime_formatted"] = pd.to_datetime(self.data[self.date_field], errors='coerce', utc=True)
        self.data["datetime_int"] = self.data["datetime_formatted"].apply(lambda x: int(x.timestamp()) if pd.notnull(x) else None)
          **A high priority filter**
        """,
        type="integer",
    ),
    AttributeInfo(
        name="username",
        description="The *case sensitive* name or ID of the message's author. **A high priority filter**",
        type="string",
    ),
    # AttributeInfo(
    #     name="ID",
    #     description="A UUID v1 generated from the timestamp of the message",
    #     type="uuid",
    # ),
    # AttributeInfo(
    #     name="PLATFORM",
    #     description="The app where the message was sent. Valid values are ['Discord', 'WhatsApp']",
    #     type="string",
    # ),
    # AttributeInfo(
    #     name="CHAT",
    #     description=f"The name of the chat room where the message was sent, will be invoked as 'the chat' or 'the chats'",
    #     type="string",
    # ),
]
document_content_description = "A conversation with a sequence of messages and their authors"
llm = ChatOpenAI(temperature=0)
retriever = SelfQueryRetriever.from_llm(
    llm,
    vectorstore,
    document_content_description,
    metadata_field_info,
    fix_invalid=True,
    enable_limit=True,
    use_original_query=True,
    verbose=True
)

model_responses = []

logging.basicConfig()
logging.getLogger("langchain.retrievers.self_query").setLevel(logging.INFO)

docs = retriever.invoke("What are some recent messages from Krishna Saxena? Today is 2025-01-01 00:00:00")
# docs = retriever.invoke("What are some messages Krishna Saxena from between 2024-01-01 00:00:00 and 2025-01-05 00:00:00?")
#     # len(unique_docs)
# print(docs)
# print(docs)
#     sys_msg = """
#         You have been given a question and a set of documents to answer the question. 
#         Provide a concise answer to the question based on the information in the documents.
#         Here is the question:
#         {question}
#         Here are the documents:
#         {documents}
#         """

#     prompt = ChatPromptTemplate.from_template(sys_msg)

#     chain = prompt | llm

#     # question = questions[0]
#     # docs = retriever.invoke(question.get("question"))
#     # print(docs)

#     # print(db.get_context(k=10, current_index=docs[0].metadata["index"]))

#     model_answer = chain.invoke({'question': question.get("question"), 'documents':docs})

#     # print(model_answer.content)
#     model_responses.append(model_answer.content)
#     print("Question: ", question.get("question"))
#     print("Model Answer: ", model_answer.content)
# # print(model_responses)
# evaluator = Evaluator(model_responses, questions)
# evaluator.evaluate()
# evaluator.save_evaluations("self_query_test.json")
# print(evaluator.average_score())