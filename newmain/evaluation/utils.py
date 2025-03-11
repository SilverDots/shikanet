from pydantic import BaseModel, Field
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import MessagesState, START, StateGraph
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import ToolNode
import json

from langchain_ollama.llms import OllamaLLM

class Evaluation(BaseModel):
    score: int = Field(..., description="The score given to the model's response")
    reasoning: str = Field(..., description="The reasoning for the score")
    model_answer: str = Field(..., description="The answer provided by the model")


sys_msg = SystemMessage(content="""
    You an agent tasked with helping users recall information from a chat history.
    You have access to a tool to retrieve a small subset of messages from a discord
    chat history using embeddings. You can use this tool to help you answer user questions.""")

eval_msg = """
    You are an agent designed to evaluate whether an answer to a prompt or question is correct or not.
    You will be given a ground-truth answer with a set of corresponding messages, and the answer provided
    by the model. Give a score 1-5 on how well the model answered the question.
    1: The answer is completely incorrect or the model could not find any answer. For example, the answer is "I don't know."
    or if the correct answer is "The sky is blue," the model's answer is "The sky is green."
    2: The answer is vague and doesn't include any specific information. For example, the correct answer is "The sky is blue,"
    but the model's answer is "The sky is a color."
    3: The answer includes part of the correct information or references the correct information but is not complete.
    For example, the correct answer is "The sky is blue and the grass is green," but the model's answer is "The sky is blue."
    4: The answer is mostly correct but has some minor errors or omissions. It doesn't include anything wrong, 
    but it doesn't include everything right. For example, the correct answer is "The sky is light blue,"
    but the model's answer is "The sky is blue."
    5: The answer is completely correct and includes all relevant information. No errors or omissions.
    For example, the correct answer is "The sky is blue," and the model's answer is "The sky is blue."
    Here is the question:
    {question}
    Here is the response provided by the model:
    {model_response}
    Here is the ground-truth answer:
    {ground_truth}
    Here are the ground_truth supporting messages:
    {ground_truth_supporting_messages}
    Provide reasoning for your score.
"""