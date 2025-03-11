from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import MessagesState, START, StateGraph
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import ToolNode
import operator
from typing import Annotated
import json


vectordb = Chroma(
    persist_directory="/Users/kastenwelsh/Documents/cse481-p/.data/vectorDB",
    collection_name="openai_0.0.2",
    embedding_function=OpenAIEmbeddings(),
)


question = "What did spidersnrhap plan to do on his birthday, according to the message from January 25, 2025?"
llm = ChatOpenAI(temperature=0)
retriever_from_llm = MultiQueryRetriever.from_llm(
    retriever=vectordb.as_retriever(), llm=llm
)

# Set logging for the queries
import logging

logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

unique_docs = retriever_from_llm.invoke(question)
len(unique_docs)
print(len(unique_docs))


# class OverallState(MessagesState):
#     original_question: str = Field(..., description="The original question to answer")
#     prompts: List[str] = Field(..., description="The generated prompts to answer the question")

# class QueryState(MessagesState):
#     query: str = Field(..., description="The query to retrieve relevant documents")

# def generateQueriesd

# def continue_to_retrieve(state: OverallState):
#     return [Send("generate_answer")]