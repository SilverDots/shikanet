DATA_FILE = "../data/WhatsAppCleaned/WhatsAppCombined.tsv"
OUTPUT_JSON_FILE = '../data/WhatsAppCleaned/WhatsAppCombined.json'
COLLECTION_NAME = 'timescale_WA_v1'

LLAMA_3B_NAME = 'llama3.2'

from datetime import datetime, timedelta
import os

import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from timescale_vector import client
from langchain_community.document_loaders.json_loader import JSONLoader
from langchain_community.vectorstores.timescalevector import TimescaleVector
from langchain_ollama import OllamaEmbeddings

def add_context(chat_df, col_to_cat='MESSAGE', new_col_name='CONTEXTUALIZED_MESSAGE', context_len=3, author_col='SENDER'):
  temp_col = col_to_cat+'_TMP'
  chat_df[temp_col] = chat_df[author_col] + ' ~ ' + chat_df[col_to_cat]

  neg_cols_added = [f'{temp_col}_neg_{i}' for i in range(1, 1 + context_len)]
  plus_cols_added = [f'{temp_col}_plus_{i}' for i in range(1, 1 + context_len)]

  for i in range(1, context_len + 1):
    chat_df[f'{temp_col}_plus_{i}'] = chat_df[temp_col].shift(-i)
    chat_df[f'{temp_col}_neg_{i}'] = chat_df[temp_col].shift(i)

  chat_df[new_col_name] = chat_df[[*neg_cols_added, temp_col, *plus_cols_added]].fillna('').agg('\n'.join,
                                                                                                axis=1).str.strip()
  chat_df.drop(columns=[temp_col, *neg_cols_added, *plus_cols_added], inplace=True)
  return chat_df

def create_uuid(date_string: str):
  if date_string is None:
    return None
  # 2024-02-24T17:30:00.000
  time_format = "%Y-%m-%dT%H:%M:%S.%f"
  datetime_obj = datetime.strptime(date_string, time_format)
  uuid = client.uuid_from_time(datetime_obj)
  return str(uuid)

def extract_metadata(record, metadata) -> dict:
  # metadata = dict()
  metadata["ID"] = create_uuid(record["DATETIME"])
  metadata["MSG_ID"] = record["MSG_ID"]
  metadata["DATETIME"] = record["DATETIME"] #datetime.strftime(record["DATETIME"], '%Y-%m-%d %H:%M')
  metadata["MESSAGE"] = record["MESSAGE"]
  metadata["SENDER"] = record["SENDER"]
  metadata["PLATFORM"] = record["PLATFORM"]
  metadata["CHAT"] = record["CHAT"]

  del metadata['source']
  del metadata['seq_num']
  return metadata

if __name__ == '__main__':
  data = pd.read_csv(DATA_FILE, sep='\t', parse_dates=['DATETIME'])
  data = add_context(data, col_to_cat='MESSAGE', new_col_name='CONTEXTUALIZED_MESSAGE', context_len=3)
  # save to JSON so it can be read by timestore
  data.to_json(OUTPUT_JSON_FILE, 'table', index=False)

  # Load data from JSON file and extract metadata
  loader = JSONLoader(
    file_path='../data/WhatsAppCleaned/WhatsAppCombined.json',
    jq_schema=".data[]",
    content_key='CONTEXTUALIZED_MESSAGE',
    text_content=True,
    metadata_func=extract_metadata,
  )

  documents = loader.load()
  print('# Documents', len(documents), 'Example Document:')
  print(documents[0])

  embed_model = OllamaEmbeddings(model=LLAMA_3B_NAME)

  # Create a Timescale Vector instance from the collection of documents
  db = TimescaleVector.from_documents(
    embedding=embed_model,
    ids=[doc.metadata["ID"] for doc in documents],
    documents=documents,
    collection_name=COLLECTION_NAME,
    service_url=os.environ['TIMESCALE_SERVICE_URL'],
    time_partition_interval=timedelta(days=7),
  )