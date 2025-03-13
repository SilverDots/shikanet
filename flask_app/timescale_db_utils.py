LLAMA_3B_NAME = 'llama3.2'

import os
from datetime import datetime
from logging import getLogger

os.environ["GOOGLE_API_KEY"] = os.environ["API_KEY"]
logger = getLogger(__name__)

import pandas as pd
import numpy as np
from dotenv import load_dotenv
load_dotenv()

DATA_FILE = os.environ['LOCAL_DATA_FILE']
COLLECTION_NAME = os.environ['TIMESCALE_COLLECTION_NAME']
COLLECTION_NAME_SUMM = os.environ['TIMESCALE_COLLECTION_NAME_SUMM']

from langchain_community.vectorstores.timescalevector import TimescaleVector
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_community.query_constructors.timescalevector import TimescaleVectorTranslator
from typing import List
from types import MethodType
from pydantic import BaseModel, Field

### Data
data = pd.read_csv(DATA_FILE, sep='\t', parse_dates=['DATETIME'])

### LLMs
small_llm = ChatOllama(model=LLAMA_3B_NAME, temperature=0.)
big_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    timeout=None
)
ret_llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    timeout=None
)

embed_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
chunk_embed_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

vector_db = TimescaleVector(
  collection_name=COLLECTION_NAME,
  service_url=os.environ['TIMESCALE_SERVICE_URL'],
  embedding=embed_model,
)

vector_db_summ = TimescaleVector(
    collection_name=COLLECTION_NAME_SUMM,
    service_url=os.environ['TIMESCALE_SERVICE_URL'],
    embedding=embed_model,
)


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

  within_context_df = data[(data.index >= context_lo)&(data.index <= context_hi)].copy()
  within_context_df['VERBOSE'] = within_context_df['DATETIME'].dt.strftime('%A %B %d, %Y %H:%M') + '\t' + \
                                 within_context_df['SENDER'] + ' ~ ' + within_context_df['MESSAGE']

  return within_context_df['VERBOSE'].str.cat(sep='\n')

def retrieve_more_context_summ(msg_id, platform, chat, context_len=5):
  """
  Given a message with ID `msg_id`, get the `addl_msgs` preceding and following messages for context

  :param msg_id: the ID of a retrieved message
  :param platform: the platform of the retrieved message
  :param chat: the chat of the retrieved message
  :param n_addl_msgs: number of additional messages before and after msg `msg_id` to retrieve
  :param context_len: the number of messages after `msg_id` in the LLM determined context
  :return: a string
  """
  msg_info = data[data['MSG_ID'] == msg_id]

  chat_hist = data[
      (data['PLATFORM'] == platform) &
      (data['CHAT'] == chat)
  ]

  addl_msgs_1 = (3, 5) # for a llm determined context of size 3 msgs, grab 5 before and after
  addl_msgs_2 = (5, 3) # for a llm determined context of size 5 msgs, grab 3 before and after
  # find an eqn n_addl = A*exp(-lambda*context_win_len)
  lam = (np.log(addl_msgs_1[1]) - np.log(addl_msgs_2[1]))/(np.log(addl_msgs_2[0]) - np.log(addl_msgs_1[0]))
  A = np.exp(np.log(addl_msgs_1[1]) + lam*np.log(addl_msgs_1[0]))
  n_addl_msgs = int(np.ceil(A*np.exp(-lam*context_len)))

  context_lo = max(chat_hist.index[0], msg_info.index[0] - n_addl_msgs)
  context_hi = min(chat_hist.index[-1], msg_info.index[0] + context_len + n_addl_msgs)

  within_context_df = data[(data.index >= context_lo)&(data.index <= context_hi)].copy()
  within_context_df['VERBOSE'] = within_context_df['DATETIME'].dt.strftime('%A %B %d, %Y %H:%M') + '\t' + within_context_df['SENDER'] + ' ~ ' + within_context_df['MESSAGE']

  return within_context_df['VERBOSE'].str.cat(sep='\n')

def format_docs(docs):
  return "\n".join(
    f"<conv{i + 1}>:\nSource:{doc['MSG_ID']}\nContent:{doc['FULL_CONTEXT']}\n</conv{i + 1}>\n" for i, doc in
    enumerate(docs)
  )

# Prompts
#   Grader
class GradeDocuments(BaseModel):
  """Binary score for relevance check on retrieved documents."""

  binary_score: str = Field(
    description="Documents are relevant to the question, 'yes' or 'no'"
  )

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
result_system = """You are an assistant for question-answering tasks. Answer the question based upon the given conversation snippets.
Use three-to-five sentences maximum and keep the answer concise."""
result_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", result_system),
        ("human", "Retrieved conversation: \n\n <convs>{conversations}</convs> \n\n User question: <question>{question}</question>"),
    ]
)

# Chains
res_rag_chain = result_prompt | big_llm | StrOutputParser()

# Retriever models
def my_get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> List[Document]:
  """Get documents relevant for a query.

  Args:
      query: string to find relevant documents for

  Returns:
      List of relevant documents
  """
  structured_query = self.query_constructor.invoke(
    {"query": query}, config={"callbacks": run_manager.get_child()}
  )
  if self.verbose:
    logger.info(f"Generated Query: {structured_query}")
  new_query, search_kwargs = self._prepare_query(query, structured_query)
  # ################# BEGIN: MY INTRODUCTION #################
  # Double the requested message count, and return at least 10
  search_kwargs['k'] = search_kwargs.get('k', 10)
  search_kwargs['k'] = search_kwargs['k'] * 2
  if search_kwargs['k'] < 10:
    search_kwargs['k'] = 10
  if self.verbose:
    logger.info(f"Final Query: {new_query} with args {search_kwargs}")
  # #################  END: MY INTRODUCTION  #################
  docs = self._get_docs_with_query(new_query, search_kwargs)
  return docs

metadata_field_info_summ = [
  AttributeInfo(
    name="DATETIME",
    description="The time the message was sent. **A high priority filter**",
    type="timestamp",
  ),
  AttributeInfo(
    name="ID",
    description="A UUID v1 generated from the timestamp of the message",
    type="uuid",
  ),
  AttributeInfo(
    name="PLATFORM",
    description="The app where the message was sent. Valid values are ['Discord', 'WhatsApp']",
    type="string",
  ),
  AttributeInfo(
    name="CHAT",
    description=f"The name of the chat room where the message was sent, will be invoked using keywords 'the chat' or 'the chats'. Valid values are [{[f'\'{name}\'' for name in sorted(data.CHAT.unique())]}]",
    type="string",
  ),
]
document_content_description_summ = "Information about message chains"

retriever_summ = SelfQueryRetriever.from_llm(
  ret_llm,
  vector_db_summ,
  document_content_description_summ,
  metadata_field_info_summ,
  structured_query_translator=TimescaleVectorTranslator(),
  enable_limit=True,
  use_original_query=True,
  verbose=True
)
retriever_summ._get_relevant_documents = MethodType(my_get_relevant_documents, retriever_summ)


def answer_user_question_timescale(question):
  # ******************* STEP 1: Retrieve Documents *******************
  # start_dt = datetime(2025, 1, 1)  # Start date = Jan 1, 2025
  # end_dt = datetime.now()  # End date = today
  retriever = vector_db.as_retriever(
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
    # TODO: find out why res is None
    if res and res.binary_score == 'yes':
      docs_to_use.append({'MSG_ID': msg_id, 'FULL_CONTEXT': msg_context})

  # ******************* STEP 4: Generate Result *******************
  generation = res_rag_chain.invoke({"conversations":format_docs(docs_to_use), "question": question})
  return generation

def answer_user_question_ts_self_query(question):
  # ******************* STEP 1: Retrieve Documents *******************
  # start_dt = datetime(2025, 1, 1)  # Start date = Jan 1, 2025
  # end_dt = datetime.now()  # End date = today
  # Give LLM info about the metadata fields
  metadata_field_info = [
    AttributeInfo(
      name="DATETIME",
      description="The time the message was sent. **A high priority filter**",
      type="timestamp",
    ),
    AttributeInfo(
      name="SENDER",
      description="The *case sensitive* name or ID of the message's author. **A high priority filter**",
      type="string",
    ),
    AttributeInfo(
      name="ID",
      description="A UUID v1 generated from the timestamp of the message",
      type="uuid",
    ),
    AttributeInfo(
      name="PLATFORM",
      description="The app where the message was sent. Valid values are ['Discord', 'WhatsApp']",
      type="string",
    ),
    AttributeInfo(
      name="CHAT",
      description=f"The name of the chat room where the message was sent, will be invoked as 'the chat' or 'the chats'. Valid values are [{[f'\'{name}\'' for name in sorted(data.CHAT.unique())]}]",
      type="string",
    ),
  ]
  document_content_description = "A conversation with a sequence of messages and their authors"

  # Instantiate the self-query retriever from an LLM

  retriever = SelfQueryRetriever.from_llm(
    ret_llm,
    vector_db,
    document_content_description,
    metadata_field_info,
    structured_query_translator=TimescaleVectorTranslator(),
    enable_limit=True,
    use_original_query=True,
    verbose=True
  )
  retriever._get_relevant_documents = MethodType(my_get_relevant_documents, retriever)

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
    if res and res.binary_score == 'yes':
      docs_to_use.append({'MSG_ID': msg_id, 'FULL_CONTEXT': msg_context})

  # ******************* STEP 4: Generate Result *******************

  # Run
  generation = res_rag_chain.invoke({"conversations":format_docs(docs_to_use), "question": question})
  return generation

def answer_user_question_sem_chunk(question):
  # ******************* STEP 1: Retrieve Documents *******************
  # Give LLM info about the metadata fields

  docs = retriever_summ.invoke(question)

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
    if res and res.binary_score == 'yes':
      docs_to_use.append({'MSG_ID': msg_id, 'FULL_CONTEXT': msg_context})

  # ******************* STEP 4: Generate Result *******************

  # Chain
  generation = res_rag_chain.invoke({"conversations":format_docs(docs_to_use), "question": question})
  return generation