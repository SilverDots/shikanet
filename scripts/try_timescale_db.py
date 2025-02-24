question = "What were the last 5 ToDos papa gave?"

LLAMA_3B_NAME = 'llama3.2'
DATA_FILE = "../data/WhatsAppCleaned/WhatsAppCombined.tsv"
COLLECTION_NAME = 'timescale_WA_v1'

import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from langchain_community.vectorstores.timescalevector import TimescaleVector
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


def retrieve_more_context(data, msg_id, platform, chat, n_addl_msgs=10):
  """
  Given a message with ID `msg_id`, get the `addl_msgs` preceding and following messages for context

  :param data: a DataFrame of message info
  :param msg_id: the ID of a retrieved message
  :param platform: the platform of the retrieved message
  :param chat: the chat of the retrieved message
  :param n_addl_msgs: number of additional messages before and after msg `msg_id` to retrieve
  :return: a string
  """
  msg_info = data[data['MSG_ID'] == msg_id]

  chat_hist = data[
    (data['PLATFORM'] == platform) &
    (data['CHAT'] == chat)
    ]

  context_lo = max(chat_hist.index[0], msg_info.index[0] - n_addl_msgs)
  context_hi = min(chat_hist.index[-1], msg_info.index[0] + n_addl_msgs)

  within_context_df = data.iloc[context_lo:context_hi, :].copy()
  within_context_df['VERBOSE'] = within_context_df['PLATFORM'] + ' : ' + within_context_df['CHAT'] + '\t' + \
                                 within_context_df['DATETIME'].dt.strftime('%A %B %d, %Y %H:%M') + '\t' + \
                                 within_context_df['SENDER'] + ' ~ ' + within_context_df['MESSAGE']

  return within_context_df['VERBOSE'].str.cat(sep='\n')

# Data model
class GradeDocuments(BaseModel):
  """Binary score for relevance check on retrieved documents."""

  binary_score: str = Field(
    description="Documents are relevant to the question, 'yes' or 'no'"
  )
# Prompts
#   Grader
grader_system = """You are a grader assessing relevance of a retrieved document to a user question. \n
    If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
grade_prompt = ChatPromptTemplate.from_messages(
  [
    ("system", grader_system),
    ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
  ]
)
#   Result
result_system = """You are an assistant for question-answering tasks. Answer the question based upon your knowledge.
Use three-to-five sentences maximum and keep the answer concise."""
result_prompt = ChatPromptTemplate.from_messages(
  [
    ("system", result_system),
    ("human", "Retrieved documents: \n\n <docs>{documents}</docs> \n\n User question: <question>{question}</question>"),
  ]
)

if __name__ == '__main__':
  data = pd.read_csv(DATA_FILE, sep='\t', parse_dates=['DATETIME'])
  big_llm = ChatOllama(model=LLAMA_3B_NAME)
  embed_model = OllamaEmbeddings(model=LLAMA_3B_NAME)
  db = TimescaleVector(
      collection_name=COLLECTION_NAME,
      service_url=os.environ['TIMESCALE_SERVICE_URL'],
      embedding=embed_model,
  )

  # ******************* STEP 1: Retrieve Documents *******************
  # start_dt = datetime(2025, 1, 1)  # Start date = Jan 1, 2025
  # end_dt = datetime.now()  # End date = today
  retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={'k': 10}
    # search_kwargs={"start_date": start_dt, "end_date": end_dt, 'k': 10}
  )
  docs = retriever.invoke(question)

  # ******************* STEP 2: Add more Context *******************
  fuller_context = [
    (
      doc.metadata['MSG_ID'],
      retrieve_more_context(data, doc.metadata['MSG_ID'], doc.metadata['PLATFORM'], doc.metadata['CHAT'])
    )
    for doc in docs
  ]

  # ******************* STEP 3: Grade Document Relevancy *******************
  # LLM with function call
  structured_llm_grader = big_llm.with_structured_output(GradeDocuments)

  retrieval_grader = grade_prompt | structured_llm_grader

  docs_to_use = []

  for (msg_id, msg_context) in fuller_context:
    print(msg_context, '\n', '-' * 50)
    res = retrieval_grader.invoke({"question": question, "document": msg_context})
    print(res, '\n\n\n')
    if res.binary_score == 'yes':
      docs_to_use.append({'MSG_ID': msg_id, 'FULL_CONTEXT': msg_context})

  # ******************* STEP 4: Generate Result *******************

  # Post-processing
  def format_docs(docs):
      return "\n".join(f"<doc{i+1}>:\nSource:{doc['MSG_ID']}\nContent:{doc['FULL_CONTEXT']}\n</doc{i+1}>\n" for i, doc in enumerate(docs))

  # Chain
  rag_chain = result_prompt | big_llm | StrOutputParser()

  # Run
  generation = rag_chain.invoke({"documents":format_docs(docs_to_use), "question": question})
  print('******************* Generation *******************')
  print(generation)