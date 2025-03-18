LLAMA_3B_NAME = 'llama3.2'

import os
from datetime import datetime
from logging import getLogger

from dotenv import load_dotenv
from functools import partial
load_dotenv()

os.environ["GOOGLE_API_KEY"] = os.environ["API_KEY"]
logger = getLogger(__name__)

import pandas as pd
import numpy as np

DATA_FILE = os.environ['LOCAL_DATA_FILE']
COLLECTION_NAME = os.environ['TIMESCALE_COLLECTION_NAME']
COLLECTION_NAME_SUMM = os.environ['TIMESCALE_COLLECTION_NAME_SUMM']

from langchain_community.vectorstores.timescalevector import TimescaleVector
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
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
data.dropna(inplace=True)

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

vector_db = TimescaleVector(
  collection_name=COLLECTION_NAME,
  service_url=os.environ['TIMESCALE_SERVICE_URL'],
  embedding=embed_model,
)

print('COLLECTION_NAME_SUMM', COLLECTION_NAME_SUMM)
vector_db_summ = TimescaleVector(
    collection_name=COLLECTION_NAME_SUMM,
    service_url=os.environ['TIMESCALE_SERVICE_URL'],
    embedding=embed_model,
)

### Helper functions
def get_metadata_dict(within_context_df):
  meta_dicts = []
  for _, row in within_context_df.iterrows():
    meta_dicts.append(
      {
        'SENDER': row['SENDER'],
        'DATETIME': row['DATETIME'],
        'MESSAGE': row['MESSAGE'],
        'PLATFORM': row['PLATFORM'],
        'CHAT': row['CHAT']
      }
    )
  return meta_dicts

def format_docs(docs):
  return "\n".join(
    f"<conv{i + 1}>:\nSource:{doc['MSG_ID']}\nContent:{doc['FULL_CONTEXT']}\n</conv{i + 1}>\n" for i, doc in
    enumerate(docs)
  )

def highlight_segment(source, segment, hl_start_symbol='**', hl_end_symbol='**'):
  """
  :param hl_start_symbol: '<mark>' recommended, '**' default
  :param hl_end_symbol: '</mark>' recommended, '**' default
  """
  highlight_index = source.find(segment)
  return source[:highlight_index] + hl_start_symbol + source[highlight_index:highlight_index + len(segment)] + hl_end_symbol + source[highlight_index + len(segment):] if highlight_index >= 0 else source

def replace_aliases(df, str_col, user_aliases, friend_aliases):
  for alias, name in user_aliases.items():
    df[str_col] = df[str_col].str.replace(alias, name)
  for alias, name in friend_aliases.items():
    df[str_col] = df[str_col].str.replace(alias, name)

### Context retrieval functions
def retrieve_more_context(data, msg_id, platform, chat, user_aliases, friend_aliases, n_addl_msgs=10):
  """
  Given a message with ID `msg_id`, get the `addl_msgs` preceding and following messages for context

  :param data: a DataFrame of message info
  :param msg_id: the ID of a retrieved message
  :param platform: the platform of the retrieved message
  :param chat: the chat of the retrieved message
  :param n_addl_msgs: number of additional messages before and after msg `msg_id` to retrieve
  :return: a string of concatenated messages, a list of metadata dicts for each message in `msg_id`'s context
  """
  msg_info = data[data['MSG_ID'] == msg_id]

  chat_hist = data[
    (data['PLATFORM'] == platform) &
    (data['CHAT'] == chat)
  ]

  context_lo = max(chat_hist.index[0], msg_info.index[0] - n_addl_msgs)
  context_hi = min(chat_hist.index[-1], msg_info.index[0] + n_addl_msgs)

  within_context_df = data[(data.index >= context_lo) & (data.index <= context_hi)].copy()
  replace_aliases(within_context_df, 'MESSAGE', user_aliases, friend_aliases)
  within_context_df['VERBOSE'] = within_context_df['DATETIME'].dt.strftime('%A %B %d, %Y %H:%M') + '\t' + \
                                 within_context_df['SENDER'] + ' ~ ' + within_context_df['MESSAGE']

  return within_context_df['VERBOSE'].str.cat(sep='\n'), get_metadata_dict(within_context_df)

def retrieve_more_context_summ(data, msg_id, platform, chat, user_aliases, friend_aliases, context_len=5):
  """
  Given a message with ID `msg_id`, get the `addl_msgs` preceding and following messages for context

  :param msg_id: the ID of a retrieved message
  :param platform: the platform of the retrieved message
  :param chat: the chat of the retrieved message
  :param n_addl_msgs: number of additional messages before and after msg `msg_id` to retrieve
  :param context_len: the number of messages after `msg_id` in the LLM determined context
  :return: a string of concatenated messages, a list of metadata dicts for each message in `msg_id`'s context
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

  within_context_df = data[(data.index >= context_lo) & (data.index <= context_hi)].copy()
  replace_aliases(within_context_df, 'MESSAGE', user_aliases, friend_aliases)
  within_context_df['VERBOSE'] = within_context_df['DATETIME'].dt.strftime('%A %B %d, %Y %H:%M') + '\t' + within_context_df['SENDER'] + ' ~ ' + within_context_df['MESSAGE']

  return within_context_df['VERBOSE'].str.cat(sep='\n'), get_metadata_dict(within_context_df)

### Prompts
#   Relevance Grader
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
#   Result Summarize
result_system = """You are an assistant for question-answering tasks. Answer the question based upon the given conversation snippets.
Use three-to-five sentences maximum and keep the answer concise."""
result_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", result_system),
        ("human", "Retrieved conversation: \n\n <convs>{conversations}</convs> \n\n User question: <question>{question}</question>"),
    ]
)

#   Hallucination Checker
class GradeHallucinations(BaseModel):
  """Binary score for hallucination present in 'generation' answer."""

  binary_score: str = Field(
    ...,
    description="Answer is grounded in the facts, 'yes' or 'no'"
  )

hallucination_system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n
Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
hallucination_prompt = ChatPromptTemplate.from_messages(
  [
    ("system", hallucination_system),
    ("human",
     "Set of facts: \n\n <facts>{documents}</facts> \n\n LLM generation: <generation>{generation}</generation>"),
  ]
)

#   Highlighter
class HighlightDocuments(BaseModel):
  """Return the specific part of a document used for answering the question."""

  Source: List[str] = Field(
    ...,
    description="List of alphanumeric ID of docs used to answers the question"
  )
  Content: List[str] = Field(
    ...,
    description="List of complete conversation contexts that answers the question"
  )
  Segment: List[str] = Field(
    ...,
    description="List of pointed, direct segments from used documents that answer the question"
  )

highlight_parser = PydanticOutputParser(pydantic_object=HighlightDocuments)
highlight_system = """You are an advanced assistant for document search and retrieval. You are provided with the following:
1. A question.
2. A generated answer based on the question.
3. A set of conversation snippets that were referenced in generating the answer.

Your task is to identify and extract the exact inline segments from the provided conversations snippets that directly correspond to the content used to
generate the given answer. The extracted segments must be verbatim snippets from the conversations, ensuring a word-for-word match with the text
in the provided conversations.

Ensure that:
- (Important) Each conversation is an exact match to a part of the document and is fully contained within the document text.
- The relevance of each conversation to the generated answer is clear and directly supports the answer provided.
- (Important) If you didn't used the specific conversation don't mention it.

Used conversation snippets: <conv>{conversations}</conv> \n\n User question: <question>{question}</question> \n\n Generated answer: <answer>{generation}</answer>

<format_instruction>
{format_instructions}
</format_instruction>
"""

highlight_prompt = PromptTemplate(
  template=highlight_system,
  input_variables=["conversations", "question", "generation"],
  partial_variables={"format_instructions": highlight_parser.get_format_instructions()},
)

#   Usefulness Grader
class GradeUsefulness(BaseModel):
  binary_score: str = Field(
    ...,
    description="This is a helpful answer for the question, 'yes' or 'no'"
  )

usefulness_llm_grader = big_llm.with_structured_output(GradeUsefulness)

usefulness_system = """You are a grader assessing whether an LLM generation is a helpful answer to a user's question.
Give a binary score 'yes' or 'no'. 'Yes' means that whoever asked the question would consider the generation to be a specific, helpful answer to their question."""
usefulness_prompt = ChatPromptTemplate.from_messages(
  [
    ("system", usefulness_system),
    ("human", "Question: <question>{question}</question> \n\n LLM generation: <generation>{generation}</generation>"),
  ]
)

# Chains
res_rag_chain = result_prompt | big_llm | StrOutputParser()
hallucination_grader = hallucination_prompt | big_llm.with_structured_output(GradeHallucinations)
doc_lookup = highlight_prompt | big_llm | highlight_parser
usefulness_grader = usefulness_prompt | usefulness_llm_grader

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
    print(f"Generated Query: {structured_query}")
  new_query, search_kwargs = self._prepare_query(query, structured_query)
  # ################# BEGIN: MY INTRODUCTION #################
  # Double the requested message count, and return at least 10
  search_kwargs['k'] = search_kwargs.get('k', 10)
  search_kwargs['k'] = search_kwargs['k'] * 2
  if search_kwargs['k'] < 10:
    search_kwargs['k'] = 10
  if self.verbose:
    print(f"Final Query: {new_query} with args {search_kwargs}")
  # #################  END: MY INTRODUCTION  #################
  docs = self._get_docs_with_query(new_query, search_kwargs)
  return docs

METADATA_FIELD_INFO = [
  AttributeInfo(
    name="DATETIME",
    description="The time the message was sent. Formatted as %Y-%m-%d %H:%M:%S-0800 **A high priority filter**",
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
    description=f"The name of the chat room where the message was sent, will be invoked when keywords 'the chat' or 'the chats' are in the query. Valid values are [{[f'\'{name}\'' for name in sorted(data.CHAT.unique())]}]",
    type="string",
  ),
]
METADATA_FIELD_INFO_SUMM = [
  AttributeInfo(
    name="DATETIME",
    description="The time the message was sent. Formatted as %Y-%m-%d %H:%M:%S-0800 **A high priority filter**",
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
    description=f"The name of the chat room where the message was sent, will be invoked when keywords 'the chat' or 'the chats' are in the query. Valid values are [{[f'\'{name}\'' for name in sorted(data.CHAT.unique())]}]",
    type="string",
  ),
]
document_content_description_summ = "Information about message chains"

def check_for_hallucination(docs_to_use, generation):
  hallucination_response = hallucination_grader.invoke(
    {"documents": format_docs(docs_to_use), "generation": generation})
  return hallucination_response.binary_score if hallucination_response else 'UNK'

def check_usefulness(question, generation):
  usefulness_response = usefulness_grader.invoke(
    {"question": question, "generation": generation})
  return usefulness_response.binary_score if usefulness_response else 'UNK'

def no_docs_output():
  """
  What to return when no docs were found
  :return:
  """
  return '', 'yes', []

def format_retrieved_docs(question, docs, retrieve_more_context_fn, user_aliases, friend_aliases):
  if len(docs) == 0:
    return no_docs_output()

  # ******************* STEP 2: Add more Context *******************
  fuller_context = [
    (
      doc.metadata['MSG_ID'],
      *retrieve_more_context_fn(data, doc.metadata['MSG_ID'], doc.metadata['PLATFORM'], doc.metadata['CHAT'], user_aliases, friend_aliases)
    )
    for doc in docs
  ]

  # ******************* STEP 3: Grade Document Relevancy *******************
  # LLM with function call
  structured_llm_grader = big_llm.with_structured_output(GradeDocuments)

  retrieval_grader = grade_prompt | structured_llm_grader

  docs_to_use = []

  for (msg_id, msg_context, metadata) in fuller_context:
    print(msg_context, '\n', '-' * 50)
    res = retrieval_grader.invoke({"question": question, "document": msg_context})
    print(res, '\n\n\n')
    if res and res.binary_score == 'yes':
      docs_to_use.append({'MSG_ID': msg_id, 'FULL_CONTEXT': msg_context, 'METADATA': metadata})

  # ******************* STEP 4: Generate Result *******************
  generation = res_rag_chain.invoke({"conversations":format_docs(docs_to_use), "question": question})

  # ******************* STEP 5: Check for hallucination *******************
  hallucination_code = check_for_hallucination(docs_to_use, generation)

  # ******************* STEP 6: Highlight quotes *******************
  lookup_response = doc_lookup.invoke(
    {"conversations": format_docs(docs_to_use), "question": question, "generation": generation}
  )

  if lookup_response:
    for id, source, segment in zip(lookup_response.Source, lookup_response.Content, lookup_response.Segment):
      id_match = -1
      for i in range(len(docs_to_use)):
        if docs_to_use[i]['MSG_ID'] == id:
          id_match = i
          break
      if id_match == -1:
        continue

      docs_to_use[id_match]['FULL_CONTEXT'] = highlight_segment(source, segment)
      for doc_i_md in docs_to_use[id_match]['METADATA']:
        doc_i_md['MESSAGE'] = highlight_segment(doc_i_md['MESSAGE'], segment)

  return generation, hallucination_code, [doc['METADATA'] for doc in docs_to_use]

def answer_user_question_timescale(question, start_dt, end_dt, user_aliases, friend_aliases):
  # ******************* STEP 1: Retrieve Documents *******************
  # start_dt = datetime(2025, 1, 1)  # Start date = Jan 1, 2025
  # end_dt = datetime.now()  # End date = today
  retriever = vector_db.as_retriever(
    search_type="similarity",
    search_kwargs={"start_date": start_dt, "end_date": end_dt, 'k': 10}
  )

  docs = retriever.invoke(question)
  return format_retrieved_docs(question, docs, retrieve_more_context, user_aliases, friend_aliases)

def answer_user_question_ts_self_query(question, start_dt, end_dt, user_aliases, friend_aliases):
  document_content_description = "A conversation with a sequence of messages and their authors"

  sq_retriever = SelfQueryRetriever.from_llm(
    ret_llm,
    vector_db,
    document_content_description,
    METADATA_FIELD_INFO,
    structured_query_translator=TimescaleVectorTranslator(),
    enable_limit=True,
    use_original_query=True,
    verbose=True,
    search_kwargs={"start_date": start_dt, "end_date": end_dt, 'k': 10}
  )
  sq_retriever._get_relevant_documents = MethodType(my_get_relevant_documents, sq_retriever)

  docs = sq_retriever.invoke(question)
  return format_retrieved_docs(question, docs, retrieve_more_context, user_aliases, friend_aliases)

def answer_user_question_sem_chunk(question, start_dt, end_dt, user_aliases, friend_aliases):
  retriever = vector_db_summ.as_retriever(
    search_type="similarity",
    search_kwargs = {"start_date": start_dt, "end_date": end_dt, 'k': 10}
  )
  docs = retriever.invoke(question)
  return format_retrieved_docs(question, docs, retrieve_more_context_summ, user_aliases, friend_aliases)

def answer_user_question_sem_chunk_sq(question, start_dt, end_dt, user_aliases, friend_aliases):
  retriever_summ = SelfQueryRetriever.from_llm(
    ret_llm,
    vector_db_summ,
    document_content_description_summ,
    METADATA_FIELD_INFO_SUMM,
    structured_query_translator=TimescaleVectorTranslator(),
    enable_limit=True,
    use_original_query=True,
    verbose=True,
    search_kwargs={"start_date": start_dt, "end_date": end_dt, 'k': 10}
  )
  retriever_summ._get_relevant_documents = MethodType(my_get_relevant_documents, retriever_summ)

  docs = retriever_summ.invoke(question)
  return format_retrieved_docs(question, docs, retrieve_more_context_summ, user_aliases, friend_aliases)