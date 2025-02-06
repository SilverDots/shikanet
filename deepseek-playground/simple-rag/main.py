import streamlit as st
from streamlit_chat import message
import random
import google.generativeai as genai
import os
import chromadb
import chromadb.utils.embedding_functions as embedding_functions
from dotenv import load_dotenv
import pandas as pd


# from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_chroma import Chroma

from langchain_huggingface import HuggingFaceEmbeddings

from langchain_google_genai import GoogleGenerativeAIEmbeddings


# Initialize Hugging Face embeddings
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
# embeddings = OllamaEmbeddings(model="deepseek-r1:14b")


load_dotenv()

MAX_CONTEXT = 5 # conversational memory window.

#=====================================================#
#                      API SETUP                      #
#=====================================================#

# Gemini setup

# Replace system prompt with your own
system_prompt = "You are a helpful chatbot for parsing through discord messages."

template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""

genai.configure(api_key=os.environ["API_KEY"])

model = OllamaLLM(model="deepseek-r1:14b")

# Embedding function for vector queries
google_ef  = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=os.environ["API_KEY"])

# Vector database /!\ NOTE: must load_data.py first /!\ uncomment the following lines if you the collections

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.environ["API_KEY"])

# embeddings = OllamaEmbeddings(model="deepseek-r1:14b")
# embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

client = chromadb.PersistentClient(path="/Users/kastenwelsh/Documents/cse481-p/.data/vectorDB")
# collection = client.get_collection(name="test_chat", embedding_function=google_ef)
vector_store = Chroma(
    client = client,
    # collection_name = "test_deepseek_1",
    # collection_name="test_hug_mpnet",
    collection_name="test_google",
    embedding_function = embeddings
)

#=====================================================#
#                     Chat Code                       #
#=====================================================#

# Storing the displayed messages
if 'past' not in st.session_state:
    st.session_state['past'] = [""]

# Add default welcome message. This can be useful for introducing your chatbot
if 'generated' not in st.session_state:
    st.session_state['generated'] = [
        "I found your discord messages... tee hee! Ask me about them and I'll show you what I know!"
        ]

# Pick random avatar
if "avatars" not in st.session_state:
    st.session_state.avatars = {"user": random.randint(0,100), "bot": random.randint(0,100)}

# Storing the conversation history for the LLM
if "messages" not in st.session_state:
    st.session_state.messages = []

# llm = model.start_chat(history=st.session_state.messages)

# Function to send a message to the LLM and update the UI
def chat(user_input=""):
    if user_input == "":
        user_input = st.session_state.input
    st.session_state.input = ""
    # To use custom data, query the database here and combine it with the user input for the LLM to reference
    context = query_db(user_input, 1)
    # print(context)
    prompt = ChatPromptTemplate.from_template(template)

    chain = prompt | model

    completion = chain.invoke({"question": user_input, "context": context})

    # Add new user message to LLM message history
    st.session_state.messages.append({"role": "user", "parts": user_input})

    # Add LLM response to message history
    st.session_state.messages.append({"role": "model", "parts": completion})

    # Limit LLM message history using sliding window
    if len(st.session_state.messages) > MAX_CONTEXT:
      # keeps system call at index 0
      st.session_state.messages = st.session_state.messages[:MAX_CONTEXT]

    # Add LLM message to UI
    st.session_state.generated.append(completion + "\n" + context.replace("```", ""))
    # Add user message to UI
    st.session_state.past.append(user_input)

# Function to query the vector database
# Returns a list of dictionaries
def query_db(query, n_results=1):
    # results = collection.query(
    #     query_texts=[query],
    #     n_results=n_results
    # )
    retriever = vector_store.as_retriever(search_kwargs={"k": n_results})
    results = retriever.invoke(query)
    print(results)
    return "\n\n".join(result.page_content for result in results)


#=====================================================#
#               Font-end, yup thats it!               #
#=====================================================#

st.set_page_config(page_title="Testing 481p", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.header("Testing\n")

with st.sidebar:
    st.markdown("# About 🙌")
   

# We will get the user's input by calling the chat function
input_text = st.text_input("Input a prompt here!",
                                placeholder="Enter prompt: ", key="input", on_change=chat)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        if st.session_state['past'][i] != "":
            message(st.session_state['past'][i], is_user=True, avatar_style="adventurer",seed=st.session_state.avatars["bot"], key=str(i) + '_user')
        message(st.session_state["generated"][i],seed=st.session_state.avatars["user"] , key=str(i))