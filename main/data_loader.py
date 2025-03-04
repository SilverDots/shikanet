
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
import pandas as pd

FILE_PATH = "/Users/kastenwelsh/Documents/cse481-p/.data/dataset/nvidia_page_{number}.csv"

documents = []
ids = []

for i in range(1, 20):

    # Read the CSV file
    df = pd.read_csv(FILE_PATH.format(number=i))


    df['full_text'] = df[['author.username', 'content', 'date']].astype(str).agg(' : '.join, axis=1)

    # Prepare documents for Chroma
    for j in range(0, len(df), 100):
        documents += [Document(page_content=df['full_text'].iloc[i:i+100].str.cat(sep=' \n '))]
        ids += [f"{FILE_PATH}{index + 1}" for index in df.index]

print("CSV indexed, uploading to ChromaDB...")
print("This may take a minute...")

# Create the vector store using Chroma.from_documents with a specified collection name
vector_store = Chroma.from_documents(
    documents=documents,
    embedding=OpenAIEmbeddings(),
    persist_directory="/Users/kastenwelsh/Documents/cse481-p/.data/vectorDB",
    collection_name="openai_0.0.2"
)

print("Upload complete!")
