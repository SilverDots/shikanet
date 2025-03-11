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

# questions = json.load(open("/Users/kastenwelsh/Documents/cse481-p/newmain/test_question_1.json"))
questions = json.load(open("/Users/kastenwelsh/Documents/cse481-p/main/questions.json"))[0:5]

# db = ChatDB("openai_0.0.3")
# db = krishna_loader()
db = discord_loader()

retriever = db.retriever

llm = ChatOpenAI(model="gpt-4o")

# sys_msg = """
#     You have been given a question and a set of documents to answer the question. 
#     Provide a concise answer to the question based on the information in the documents.
#     Here is the question:
#     {question}
#     Here are the documents:
#     {documents}
#     """

# prompt = ChatPromptTemplate.from_template(sys_msg)

# chain = prompt | llm

# question = questions[0]
# docs = retriever.invoke(question.get("question"))
# print(docs)

# print(db.get_context(k=10, current_index=docs[0].metadata["index"]))

# model_answer = chain.invoke({'question': question.get("question"), 'documents':docs})

# print(model_answer.content)

# evaluator = Evaluator([model_answer.content], questions)
# evaluator.evaluate()

# testing multiquery

from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI
from data_loader.loader import discord_loader
import logging

db = discord_loader()
vectordb = db.vector_store
llm = ChatOpenAI(temperature=0)
retriever_from_llm = MultiQueryRetriever.from_llm(
    retriever=vectordb.as_retriever(), llm=llm
)

model_responses = []
for question in questions:


    # logging.basicConfig()
    # logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

    unique_docs = retriever_from_llm.invoke(question)
    # len(unique_docs)


    sys_msg = """
        You have been given a question and a set of documents to answer the question. 
        Provide a concise answer to the question based on the information in the documents.
        Here is the question:
        {question}
        Here are the documents:
        {documents}
        """

    prompt = ChatPromptTemplate.from_template(sys_msg)

    chain = prompt | llm

    # question = questions[0]
    # docs = retriever.invoke(question.get("question"))
    # print(docs)

    # print(db.get_context(k=10, current_index=docs[0].metadata["index"]))

    model_answer = chain.invoke({'question': question.get("question"), 'documents':unique_docs})

    # print(model_answer.content)
    model_responses.append(model_answer.content)
    print("Question: ", question.get("question"))
    print("Model Answer: ", model_answer.content)
# print(model_responses)
evaluator = Evaluator(model_responses, questions)
evaluator.evaluate()
evaluator.save_evaluations("evaluations_test.json")
print(evaluator.average_score())