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
# questions = json.load(open("/Users/kastenwelsh/Documents/cse481-p/main/questions.json"))[0:5]
questions = json.load(open("/Users/kastenwelsh/Documents/cse481-p/main/questions_krishna.json"))
# questions = json.load(open("/Users/kastenwelsh/Documents/cse481-p/test3.json"))[0:5]

# db = ChatDB("openai_0.0.3")
db = krishna_loader()
# db = discord_loader()

retriever = db.retriever

llm = ChatOpenAI(model="gpt-4o")

from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI
from data_loader.loader import discord_loader
import logging
import requests

# db = discord_loader()
vectordb = db.vector_store
llm = ChatOpenAI(temperature=0)
retriever_from_llm = MultiQueryRetriever.from_llm(
    retriever=vectordb.as_retriever(), llm=llm
)

model_responses = []
for question in questions:

    try:

        print(type(question.get("question")), question.get("question"))
        response = requests.post(
            "http://127.0.0.1:5000/generateTSSemChunk",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"query": question.get("question")})
        )

        if response.status_code == 200:
            print("Request successful")
        else:
            print("Request failed with status code:", response.status_code)
        # chain = prompt | llm
        model_answer = response.json()
        print(model_answer)

        model_responses.append(model_answer['response'])
        print("Question: ", question.get("question"))
        print("Model Answer: ", model_answer['response'])
    # print(model_responses)
    except Exception as e:
        # print(e)
        model_responses.append("No answer")
        print("error")
        # continue


# save model_responses to a file
with open('model_responses_krishna.json', 'w') as f:
    json.dump(model_responses, f)

# open model_responses from a file
with open('model_responses_krishna.json', 'r') as f:
    model_responses = json.load(f)
evaluator = Evaluator(model_responses, questions)
evaluator.evaluate()
evaluator.save_evaluations("evaluations_test_4.json")
print(evaluator.average_score())