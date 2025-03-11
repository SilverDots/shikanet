from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI
from data_loader.loader import discord_loader

db = discord_loader()
vectordb = db.vector_store
question = ""
llm = ChatOpenAI(temperature=0)
retriever_from_llm = MultiQueryRetriever.from_llm(
    retriever=vectordb.as_retriever(), llm=llm
)
import logging

logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

unique_docs = retriever_from_llm.invoke(question)
len(unique_docs)