# %%
import logging
import os
import re
from datetime import datetime, timedelta
from types import MethodType

from langchain_experimental.text_splitter import SemanticChunker
from langchain_core.documents import Document

import numpy as np
from pygments import highlight
from tqdm import tqdm
from dotenv import load_dotenv
from pyarrow import json_

load_dotenv()

COLLECTION_NAME_SUMM = 'timescale_WA_SC_v2'

# Set up the logger
logging.basicConfig(level=logging.INFO)

# %%
### LLMs
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
os.environ["GOOGLE_API_KEY"] = os.environ["API_KEY"]

LLAMA_3B_NAME = 'llama3.2'
DEEPSEEK_1_5B_NAME = 'deepseek-r1:1.5b'

small_llm = ChatOllama(model=LLAMA_3B_NAME, temperature=0.)
# big_llm = ChatOllama(model=LLAMA_3B_NAME, temperature=0.)
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

# embed_model = OllamaEmbeddings(model=LLAMA_3B_NAME)
embed_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
chunk_embed_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# %% [markdown]
# ###  Load Data

# %%
import pandas as pd

DATA_FILE = "../data/WhatsAppCleaned/WhatsAppCombined.tsv"

def add_context(chat_df, col_to_cat='MESSAGE', new_col_name='CONTEXTUALIZED_MESSAGE', context_len=3, author_col='SENDER', date_col=None):
  temp_col = col_to_cat+'_TMP'
  chat_df[temp_col] = chat_df[author_col] + ' ~ ' + chat_df[col_to_cat] if not date_col else \
    chat_df[author_col] + ' @ ' + chat_df[date_col].dt.strftime('%A %B %d, %Y %H:%M') + ' ~ ' + chat_df[col_to_cat]

  neg_cols_added = [f'{temp_col}_neg_{i}' for i in range(1, 1 + context_len)]
  plus_cols_added = [f'{temp_col}_plus_{i}' for i in range(1, 1 + context_len)]

  for i in range(1, context_len + 1):
    chat_df[f'{temp_col}_plus_{i}'] = chat_df[temp_col].shift(-i)
    chat_df[f'{temp_col}_neg_{i}'] = chat_df[temp_col].shift(i)

  chat_df[new_col_name] = chat_df[[*neg_cols_added, temp_col, *plus_cols_added]].fillna('').agg('\n'.join, axis=1).str.strip()
  chat_df.drop(columns=[temp_col, *neg_cols_added, *plus_cols_added], inplace=True)
  return chat_df


data = pd.read_csv(DATA_FILE, sep='\t', parse_dates=['DATETIME'])
print(data.shape)
data.dropna(inplace=True)
print(data.shape)
data = add_context(data, col_to_cat='MESSAGE', new_col_name='CONTEXTUALIZED_MESSAGE', context_len=0, date_col='DATETIME')

# %% [markdown]
# ### Create Vectorstore

# %%
text_splitter = SemanticChunker(
  embed_model,
  add_start_index=True,
  breakpoint_threshold_type='percentile',
  breakpoint_threshold_amount=90.,
  min_chunk_size=3
)

def split_text_w_indices(
    self,
    text: str,
    join_char: str = '\n'
):
    start_indices = [0]

    # Splitting the essay (by default on '.', '?', and '!')
    single_sentences_list = re.split(self.sentence_split_regex, text)

    # having len(single_sentences_list) == 1 would cause the following
    # np.percentile to fail.
    if len(single_sentences_list) == 1:
        return single_sentences_list, start_indices
    # similarly, the following np.gradient would fail
    if (
        self.breakpoint_threshold_type == "gradient"
        and len(single_sentences_list) == 2
    ):
        return single_sentences_list, start_indices
    distances, sentences = self._calculate_sentence_distances(single_sentences_list)
    if self.number_of_chunks is not None:
        breakpoint_distance_threshold = self._threshold_from_clusters(distances)
        breakpoint_array = distances
    else:
        (
            breakpoint_distance_threshold,
            breakpoint_array,
        ) = self._calculate_breakpoint_threshold(distances)

    indices_above_thresh = [
        i
        for i, x in enumerate(breakpoint_array)
        if x > breakpoint_distance_threshold
    ]

    chunks = []

    # Iterate through the breakpoints to slice the sentences
    for index in indices_above_thresh:
        # The end index is the current breakpoint
        end_index = index

        # Slice the sentence_dicts from the current start index to the end index
        group = sentences[start_indices[-1] : end_index + 1]
        combined_text = join_char.join([d["sentence"] for d in group])
        # If specified, merge together small chunks.
        if (
            self.min_chunk_size is not None
            and len(combined_text) < self.min_chunk_size
        ):
            continue
        chunks.append(combined_text)

        # Update the start index for the next group
        start_indices.append(index + 1)

    # The last group, if any sentences remain
    if start_indices[-1] < len(sentences):
        combined_text = join_char.join([d["sentence"] for d in sentences[start_indices[-1]:]])
        chunks.append(combined_text)
    return chunks, start_indices

text_splitter.split_text_w_indices = MethodType(split_text_w_indices, text_splitter)

# %%
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

class SummWithReasoning(BaseModel):
    think: str = Field(description='Think through how to summarize the messages')
    summary: str = Field(description="The final summary")

# Chain
summ_chain = big_llm.with_structured_output(SummWithReasoning)#, method='json_schema')

# %%
from timescale_vector import client

def create_uuid2(datetime_obj):
  if datetime_obj is None:
    return None
  uuid = client.uuid_from_time(datetime_obj.tz_localize('US/Pacific'))
  return str(uuid)

def create_date(dt):
    if dt is None:
        return None

    # Extract relevant information
    tz_info = dt.tz_localize('US/Pacific').utcoffset()
    tz_str = f'{"+" if tz_info.days >= 0 else "-"}{np.abs(24*tz_info.days+tz_info.seconds//3600):02}{((tz_info.seconds%3600)//60):02}'
    # Create a formatted string for the timestamptz in PostgreSQL format
    timestamp_tz_str = (
        f"{dt.year}-{dt.month:02}-{dt.day:02} {dt.hour:02}:{dt.minute:02}:{dt.second:02}{tz_str}"
    )
    return timestamp_tz_str

def extract_metadata_summarize(row, context_len):
  metadata = dict()
  metadata["id"] = create_uuid2(row["DATETIME"])
  metadata["MSG_ID"] = row["MSG_ID"]
  metadata["DATETIME"] = create_date(row["DATETIME"])
  metadata["CONTEXT_LEN"] = context_len
  metadata["PLATFORM"] = row["PLATFORM"]
  metadata["CHAT"] = row["CHAT"]

  return metadata

# %%
SUMM_MSGS_PROMPT = """Please summarize the following messages in at most three sentences, focusing on this message thread's unique events and its participants.
NEVER write polite phrases like "sure thing" or "happy to help" that would make the system reading the summary believe that it was written by a large language model.


"""

# %%
docs = []

text_splitter.sentence_split_regex = r'\n\n'

logging.basicConfig(level=logging.ERROR, force=True)
for _, df in data.groupby(['PLATFORM', 'CHAT']):
  df_groups, df_indices = text_splitter.split_text_w_indices(
    '\n\n'.join(df['CONTEXTUALIZED_MESSAGE'])
  )
  df_indices.append(df.shape[0])

  for i, group_str in tqdm(enumerate(df_groups), total=len(df_groups)):
    st_idx = df_indices[i]
    end_idx = df_indices[i+1]

    summ_response = summ_chain.invoke(SUMM_MSGS_PROMPT+group_str)

    if summ_response and summ_response.summary:
      docs.append(
        Document(
          page_content=summ_response.summary,
          metadata=extract_metadata_summarize(df.iloc[st_idx, :], end_idx-st_idx),
        )
      )
logging.basicConfig(level=logging.INFO, force=True)

# %%
from langchain_community.vectorstores.timescalevector import TimescaleVector

# Create a Timescale Vector instance from the collection of documents
db = TimescaleVector.from_documents(
  embedding=embed_model,
  ids=[doc.metadata["id"] for doc in docs],
  documents=docs,
  COLLECTION_NAME_SUMM=COLLECTION_NAME_SUMM,
  service_url=os.environ['TIMESCALE_SERVICE_URL']
)

db.drop_index()
db.create_index(index_type="tsv")

# %% [markdown]
# ### Read Vectorstore

# %%
from langchain_community.vectorstores.timescalevector import TimescaleVector
import os

db = TimescaleVector(
    collection_name=COLLECTION_NAME_SUMM,
    service_url=os.environ['TIMESCALE_SERVICE_URL'],
    embedding=embed_model,
)

# db.create_index(index_type="tsv")

# %% [markdown]
# ### Question

# %%
question = "What were the last 5 ToDos papa gave?"

# %% [markdown]
# ### Retrieve docs from DB + Add Additional Context

# %%
# from datetime import datetime
# start_dt = datetime(2025, 1, 1)  # Start date = Jan 1, 2025
# end_dt = datetime.now() # End date = 30 August 2023, 22:10:35
# td = timedelta(days=7)  # Time delta = 7 days
#
# Set timescale vector as a retriever and specify start and end dates via kwargs
retriever = db.as_retriever(
  search_type="similarity",
  search_kwargs={'k': 10}
  # search_kwargs={"start_date": start_dt, "end_date": end_dt, 'k': 10}
)

# %%
retriever.invoke(question)

# %%
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_community.query_constructors.timescalevector import TimescaleVectorTranslator

# Give LLM info about the metadata fields
metadata_field_info = [
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
document_content_description = "Information about message chains"

vectorstore = TimescaleVector(
    service_url=os.environ['TIMESCALE_SERVICE_URL'],
    embedding=embed_model,
    collection_name=COLLECTION_NAME_SUMM
)

# Instantiate the self-query retriever from an LLM

retriever = SelfQueryRetriever.from_llm(
    ret_llm,
    vectorstore,
    document_content_description,
    metadata_field_info,
    structured_query_translator=TimescaleVectorTranslator(),
    enable_limit=True,
    use_original_query=True,
    verbose=True
)

# %%
from langchain_core.callbacks.manager import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from typing import List
from types import MethodType
from logging import getLogger
logger = getLogger(__name__)

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
        search_kwargs['k'] = search_kwargs['k']*2
        if search_kwargs['k'] < 10:
          search_kwargs['k'] = 10
        if self.verbose:
            logger.info(f"Final Query: {new_query} with args {search_kwargs}")
        # #################  END: MY INTRODUCTION  #################
        docs = self._get_docs_with_query(new_query, search_kwargs)
        return docs

retriever._get_relevant_documents = MethodType(my_get_relevant_documents, retriever)

# %%
docs = retriever.invoke(question)

# %%
docs

# %%
def retrieve_more_context(msg_id, platform, chat, n_addl_msgs=10):
  """
  Given a message with ID `msg_id`, get the `addl_msgs` preceding and following messages for context

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
  within_context_df['VERBOSE'] = within_context_df['PLATFORM'] + ' : ' + within_context_df['CHAT'] + '\t' + within_context_df['DATETIME'].dt.strftime('%A %B %d, %Y %H:%M') + '\t' + within_context_df['SENDER'] + ' ~ ' + within_context_df['MESSAGE']

  return within_context_df['VERBOSE'].str.cat(sep='\n')

def retrieve_more_context_summ(msg_id, platform, chat, context_len=5):
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

  within_context_df = data[(data.index >= context_lo)&(data.index <= context_hi)].copy()
  within_context_df['VERBOSE'] = within_context_df['DATETIME'].dt.strftime('%A %B %d, %Y %H:%M') + '\t' + within_context_df['SENDER'] + ' ~ ' + within_context_df['MESSAGE']

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

  return within_context_df['VERBOSE'].str.cat(sep='\n'), meta_dicts

# %%
fuller_context = [
  (doc.metadata['MSG_ID'],
   *retrieve_more_context_summ(doc.metadata['MSG_ID'], doc.metadata['PLATFORM'], doc.metadata['CHAT'], doc.metadata['CONTEXT_LEN'])
  ) for doc in docs
]

# %% [markdown]
# ### Filter Docs w/ LLM

# %%
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

# Data model
class GradeDocuments(BaseModel):
    """Binary score for relevance check on retrieved documents."""

    binary_score: str = Field(
        description="Documents are relevant to the question, 'yes' or 'no'"
    )


# LLM with function call
# structured_llm_grader = big_llm.with_structured_output(GradeDocuments)
structured_llm_grader = small_llm.with_structured_output(GradeDocuments, method='json_schema')

# Prompt
# system = """You are a grader assessing relevance of a retrieved conversation snippet to a user's question. \n
# If **any** of the included messages contains keyword(s) or semantic meaning related to the user's question, please grade it as relevant. \n
# It does not need to be a stringent test, because your goal is to filter out erroneous retrievals **not grade for sparsity**. \n
# Please give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
system = """You are a grader assessing relevance of a retrieved document to a user question. \n
If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. \n
It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question."""
grade_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved document: \n\n {document} \n\n User question: {question}"),
    ]
)

retrieval_grader = grade_prompt | structured_llm_grader

# %%
docs_to_use = []

for (msg_id, msg_context, metadata) in fuller_context:
    print(msg_context, '\n', '-'*50)
    res = retrieval_grader.invoke({"question": question, "document": msg_context})
    print(res,'\n\n\n')
    if res and res.binary_score == 'yes':
        docs_to_use.append({'MSG_ID' : msg_id, 'FULL_CONTEXT' : msg_context, 'METADATA' : metadata})

# %%
len(docs_to_use)

# %% [markdown]
# ### Generate Result

# %%
from langchain_core.output_parsers import StrOutputParser

# Prompt
system = """You are an assistant for question-answering tasks. Answer the question based upon the given conversation snippets.
Use three-to-five sentences maximum and keep the answer concise."""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "Retrieved conversation: \n\n <convs>{conversations}</convs> \n\n User question: <question>{question}</question>"),
    ]
)

# Post-processing
def format_docs(docs):
    return "\n".join(f"<conv{i+1}>:\nSource:{doc['MSG_ID']}\nContent:{doc['FULL_CONTEXT']}\n</conv{i+1}>\n" for i, doc in enumerate(docs))

# Chain
rag_chain = prompt | big_llm | StrOutputParser()

# Run
generation = rag_chain.invoke({"conversations":format_docs(docs_to_use), "question": question})
print(generation)

# %% [markdown]
# ### Check for Hallucinations

# %%
# Data model
class GradeHallucinations(BaseModel):
    """Binary score for hallucination present in 'generation' answer."""

    binary_score: str = Field(
        ...,
        description="Answer is grounded in the facts, 'yes' or 'no'"
    )

# LLM with function call
structured_llm_grader = big_llm.with_structured_output(GradeHallucinations)

# Prompt
hallucination_system = """You are a grader assessing whether an LLM generation is grounded in / supported by a set of retrieved facts. \n
Give a binary score 'yes' or 'no'. 'Yes' means that the answer is grounded in / supported by the set of facts."""
hallucination_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", hallucination_system),
        ("human", "Set of facts: \n\n <facts>{documents}</facts> \n\n LLM generation: <generation>{generation}</generation>"),
    ]
)

hallucination_grader = hallucination_prompt | structured_llm_grader

response = hallucination_grader.invoke({"documents": format_docs(docs_to_use), "generation": generation})
print(response)

# %% [markdown]
# ### Highlight Used Docs

# %%
from typing import List
from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate

# Data model
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

# parser
highlight_parser = PydanticOutputParser(pydantic_object=HighlightDocuments)

# Prompt
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
    template= highlight_system,
    input_variables=["conversations", "question", "generation"],
    partial_variables={"format_instructions": highlight_parser.get_format_instructions()},
)

# Chain
doc_lookup = highlight_prompt | big_llm | highlight_parser

# Run
lookup_response = doc_lookup.invoke({"conversations":format_docs(docs_to_use), "question": question, "generation": generation})

# %%
from copy import deepcopy

new_docs = deepcopy(docs_to_use)

# %%
def highlight_segment(source, segment, hl_start_symbol='**', hl_end_symbol='**'):
  """
  :param hl_start_symbol: '<mark>' recommended, '**' default
  :param hl_end_symbol: '</mark>' recommended, '**' default
  """
  highlight_index = source.find(segment)
  return source[:highlight_index] + hl_start_symbol + source[highlight_index:highlight_index + len(segment)] + hl_end_symbol + source[highlight_index + len(segment):] if highlight_index >= 0 else source

# %%
for id, source, segment in zip(lookup_response.Source, lookup_response.Content, lookup_response.Segment):
  id_match = -1
  for i in range(len(new_docs)):
    if new_docs[i]['MSG_ID'] == id:
      id_match = i
      break
  if id_match == -1:
    continue

  new_docs[id_match]['FULL_CONTEXT'] = highlight_segment(source, segment, '<mark>', '</mark>')
  for doc_i_md in new_docs[id_match]['METADATA']:
    doc_i_md['MESSAGE'] = highlight_segment(doc_i_md['MESSAGE'], segment, '<mark>', '</mark>')

# %%
for doc in new_docs:
  display(HTML(doc['FULL_CONTEXT']))

# %%
for doc in new_docs:
  for doc_i_meta in doc['METADATA']:
    print(doc_i_meta['SENDER'])
    display(HTML(doc_i_meta['MESSAGE']))
    print()

# %%
for id, source, segment in zip(lookup_response.Source, lookup_response.Content, lookup_response.Segment):
    print(f"ID: {id}\nSource: {source}\nText Segment: {segment}\n")

# %%
from IPython.display import display, HTML

for id, source, segment in zip(lookup_response.Source, lookup_response.Content, lookup_response.Segment):
  highlight_index = source.find(segment)
  highlighted_source = source[:highlight_index] + '<mark>' + source[highlight_index:highlight_index + len(segment)] + '</mark>' + source[highlight_index + len(segment):]
  display(HTML(highlighted_source))


