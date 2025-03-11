from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
import pandas as pd
import chromadb


class ChatDB:

    def __init__(self,
                 collection_name,
                 data,
                 username_field,
                 content_field,
                 date_field,
                 persist_directory="/Users/kastenwelsh/Documents/cse481-p/.data/vectorDB",
                 embedding_function=OpenAIEmbeddings(),
                 other_metafields=[]
                ):
        self.username_field = username_field
        self.content_field = content_field
        self.date_field = date_field
        self.persist_directory = persist_directory
        self.embedding_function = embedding_function
        self.collection_name = collection_name
        self.other_metafields = other_metafields
        self.documents = []
        # TODO don't double up on self.data -- just do it once
        self.data = data
        self.data = self.add_datetime()
        self.vector_store = None
        self.retriever = None
        # check if any of the fields aren't in the data
        if data is not None:
            for field in [self.username_field, self.content_field, self.date_field, *self.other_metafields]:
                if field not in data.columns:
                    raise ValueError(f"Field {field} not found in data.")

    def get_context(self, k=3, current_index=0):
        df = self.data
        context = []
        for i in range(1, k + 1):
            if current_index - i >= 0 and pd.notna(df[self.content_field].iloc[current_index - i]):
                context.append(f"{df[self.username_field].iloc[current_index - i]}: {df[self.content_field].iloc[current_index - i]}")
        if pd.notna(df[self.content_field].iloc[current_index]):
            context.append(f"{df[self.username_field].iloc[current_index]}: {df[self.content_field].iloc[current_index]}")
        for i in range(1, k + 1):
            if current_index + i < len(df) and pd.notna(df[self.content_field].iloc[current_index + i]):
                context.append(f"{df[self.username_field].iloc[current_index + i]}: {df[self.content_field].iloc[current_index + i]}")
        return "\n".join(context)
    
    def get_metadata(self, record, idx):
        metadata = {}
        metadata["index"] = idx
        metadata["username"] = record[self.username_field]
        metadata["content"] = record[self.content_field]
        metadata["date"] = record[self.date_field]
        for field in self.other_metafields:
            metadata[field] = record[field]
        return metadata

    def create_documents(self, context_length=0):
        for i in range(len(self.data)):
            # if use_context:
            content = self.get_context(current_index=i, k=context_length)
            # else:
            #     content = f"{self.data[self.username_field].iloc[i]}: {self.data[self.content_field].iloc[i]}"
            metadata = self.get_metadata(self.data.iloc[i], i)
            self.documents.append(Document(page_content=content, metadata=metadata))
        return self.documents

    def upload_to_chroma(self):
        print("Uploading to ChromaDB...")
        self.vector_store = Chroma.from_documents(
                documents=self.documents,
                embedding=self.embedding_function,
                persist_directory=self.persist_directory,
                collection_name=self.collection_name
            )
        print("Upload complete!")
        return self.vector_store

    def get_chroma(self):
        persistent_client = chromadb.PersistentClient(path=self.persist_directory)
        if self.collection_name in persistent_client.list_collections():
            self.vector_store = Chroma(
                persist_directory = self.persist_directory,
                collection_name = self.collection_name,
                embedding_function = self.embedding_function
            )
        else:
            print("Collection not found in persistent storage.")
            self.upload_to_chroma()
        return self.vector_store

    def create_retriever(self, search_kwargs={"k": 1}):
        self.retriever = self.vector_store.as_retriever(search_kwargs=search_kwargs)
        return self.retriever

    def create_message_chunks(self, chunk_size=20, overlap=0):
        conversation_batches = []
        all_data = self.data[[self.username_field, self.content_field, self.date_field]]
        concat_data = all_data.apply(lambda row: ' | '.join([f"{col}: {row[col]}" for col in all_data.columns]), axis=1)
        step = chunk_size - overlap
        for i in range(0, len(self.data), step):
            end_index = i + chunk_size
            conversation_batches.append(concat_data.iloc[i:end_index].str.cat(sep=' \n '))
        return conversation_batches
    
    def add_datetime(self):
        self.data["datetime_formatted"] = pd.to_datetime(self.data[self.date_field], errors='coerce', utc=True)
        return self.data
        # # Drop rows with invalid dates
        # self.data.dropna(subset=[self.date_field], inplace=True)
        # start_time = pd.to_datetime(start_time, errors='coerce', utc=True)
        # end_time = pd.to_datetime(end_time, errors='coerce', utc=True)
        
        # return db.data[(db.data[db.date_field] >= start_time) & (db.data[db.date_field] <= end_time)]

def discord_loader():
    df_list = []
    for i in range(2, 87):
        FILE_PATH = "/Users/kastenwelsh/Documents/cse481-p/.data/dataset/nvidia_page_{number}.csv"
        curr = pd.read_csv(FILE_PATH.format(number=i))
        # keep adding to the same dataframe
        df_list.append(curr)
    df = pd.concat(df_list)

    vector_db = ChatDB("openai_0.0.8", df, "author.username", "content", "date")
    # vector_db.create_documents(context_length=3)
    # vector_db.upload_to_chroma()
    vector_db.get_chroma()
    vector_db.create_retriever()
    # vector_store = vector_db.vector_store

    # docs = vector_db.retriever.invoke("what is richard doing?")
    # print(docs)
    return vector_db

def krishna_loader():
    DATA_FILE = "data/WhatsAppCleaned/WhatsAppCombined.tsv"
    COLLECTION_NAME = 'timescale_WA_v4'

    df = pd.read_csv(DATA_FILE, sep='\t')
    df.dropna(inplace=True)
    vector_db = ChatDB(COLLECTION_NAME, df, 'SENDER', 'MESSAGE', 'DATETIME', other_metafields=['PLATFORM', 'CHAT'])
    # vector_db.create_documents(context_length=3)
    # vector_db.upload_to_chroma()
    vector_db.get_chroma()
    vector_db.create_retriever()
    vector_store = vector_db.vector_store
    # print([mes for mes in vector_db.create_message_chunks(chunk_size=5, overlap=2)[:2]])
    # docs = vector_db.retriever.invoke("hello")
    # print(docs)
    return vector_db