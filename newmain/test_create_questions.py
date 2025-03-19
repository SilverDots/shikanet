import pandas as pd
from data_loader.loader import ChatDB
from question_generator.create_questions import QuestionGenerator

DATA_FILE = "data/WhatsAppCleaned/WhatsAppCombined.tsv"
OUTPUT_JSON_FILE = 'data/WhatsAppCleaned/WhatsAppCombined.json'
COLLECTION_NAME = 'timescale_WA_v2'

df = pd.read_csv(DATA_FILE, sep='\t')
df.dropna(inplace=True)
vector_db = ChatDB(COLLECTION_NAME, df, 'SENDER', 'MESSAGE', 'DATETIME', other_metafields=['PLATFORM', 'CHAT'])
# vector_db.create_documents()
# vector_db.upload_to_chroma()
# vector_db.create_retriever()
# vector_store = vector_db.vector_store
# print([mes for mes in vector_db.create_message_chunks(chunk_size=5, overlap=2)[:2]])
# docs = vector_db.retriever.invoke("hello")
# print(docs)
question_gen = QuestionGenerator(vector_db)
question_gen.generate_questions(num_batches=100)
question_gen.save_questions("test_questions_10am.json")