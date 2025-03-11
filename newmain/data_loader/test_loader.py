import pandas as pd
from loader import ChatDB

# FILE_PATH = "/Users/kastenwelsh/Documents/cse481-p/.data/dataset/nvidia_page_{number}.csv"
# df = pd.read_csv(FILE_PATH.format(number=1))
# vector_db = ChatDB("openai_0.0.5", df, "author.username", "content", "date")
# vector_db.create_documents()
# vector_db.upload_to_chroma()
# vector_db.create_retriever()
# vector_store = vector_db.vector_store

# docs = vector_db.retriever.invoke("hello")
# print(docs)
DATA_FILE = "data/WhatsAppCleaned/WhatsAppCombined.tsv"
COLLECTION_NAME = 'timescale_WA_v3'

df = pd.read_csv(DATA_FILE, sep='\t')
df.dropna(inplace=True)
vector_db = ChatDB(COLLECTION_NAME, df, 'SENDER', 'MESSAGE', 'DATETIME', other_metafields=['PLATFORM', 'CHAT'])
vector_db.create_documents()
# vector_db.upload_to_chroma()
vector_db.get_chroma()
vector_db.create_retriever()
vector_store = vector_db.vector_store
print([mes for mes in vector_db.create_message_chunks(chunk_size=5, overlap=2)[:2]])
docs = vector_db.retriever.invoke("hello")
print(docs)