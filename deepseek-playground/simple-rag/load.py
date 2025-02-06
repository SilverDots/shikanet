import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_ollama import OllamaEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import pandas as pd

FILE_PATH = "/Users/kastenwelsh/Documents/cse481-p/.data/test_chat_1.csv"

print(f"Uploading {FILE_PATH} to ChromaDB")

load_dotenv()

# Initialize Hugging Face embeddings
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.environ["API_KEY"])

# embeddings = OllamaEmbeddings(model="deepseek-r1:14b")

# Read the CSV file
df = pd.read_csv(FILE_PATH)

# Select only the specified columns
# df = df[['id', 'author.global_name', 'author.username', 'channel_id', 'content', 'date']]
df = df[['author.username', 'content', 'date']]

# Create a new column in the df that is a concatenation of all the columns
df['full_text'] = df[['author.username', 'content', 'date']].astype(str).agg(' : '.join, axis=1)

def add_context(chat_df, col_to_cat='raw', new_col_name='full_context', context_len=3):
    neg_cols_added = [f'{col_to_cat}_neg_{i}' for i in range(1, 1+context_len)]
    plus_cols_added = [f'{col_to_cat}_plus_{i}' for i in range(1, 1+context_len)]

    for i in range(1, context_len+1):
        chat_df[f'{col_to_cat}_neg_{i}'] = chat_df[col_to_cat].shift(-i)
        chat_df[f'{col_to_cat}_plus_{i}'] = chat_df[col_to_cat].shift(i)

    chat_df[new_col_name] = chat_df[[*neg_cols_added, col_to_cat, *plus_cols_added]].fillna('').agg('\n'.join, axis=1).str.strip()
    chat_df.drop(columns=[*neg_cols_added, *plus_cols_added], inplace=True)
    return chat_df

df = add_context(df, col_to_cat='full_text', new_col_name='full_context', context_len=3)

# Prepare documents for Chroma

documents = [Document(page_content=text) for text in df['full_context'].tolist()]
ids = [f"{FILE_PATH}{index + 1}" for index in df.index]

print("CSV indexed, uploading to ChromaDB...")
print("This may take a minute...")

# Create the vector store using Chroma.from_documents with a specified collection name
vector_store = Chroma.from_documents(
    documents=documents,
    embedding=embeddings,
    persist_directory="/Users/kastenwelsh/Documents/cse481-p/.data/vectorDB",
    collection_name="test_google"
    # collection_name="test_hug_mpnet"
    # collection_name="test_deepseek_1"
)

print("Upload complete!")
# print(f"{vector_store.count()} documents in collection.")
