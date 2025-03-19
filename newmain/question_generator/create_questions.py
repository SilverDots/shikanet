import uuid
from typing import List, Optional
from typing import TypedDict

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI 

from langchain_core.prompts import ChatPromptTemplate

import pandas as pd

import json
import os


# from utils import prompt_specific, QuestionAnswerEntry

from typing import List
from pydantic import BaseModel, Field

# from utils import prompt_specific, QuestionAnswerEntry

prompt_specific = """
    Create a list of questions and answers from the following conversation.
    Give a mix of who, what, when, where, why, and how questions as applicable.
    Include names in the question if needed rather than using pronouns.
    Include some that are exactly specific, like "what show did Richard watch last week?", 
    and others that are more open-ended, like "what are some things I've done recently?"
    and "what shows have I discussed with Richard?"
    Relative terms like "last year" or "last month" can be used, but should be in reference to the last date in the data,
    {date}.
    DO NOT USE DATES OR DATETIMES IN THE QUESTION.

    Here are good example questions:

    "question": "When is Bentley's Belated Birthday party?",
    "answer": "On the 23rd",

    "question": "Did Nahum ever start reading Golden Kamuy in January?"
    "answer": "No"

    "question": "What was Kasten’s game plan in December last year?"
    "answer": "nap until 8pm
            get up and go to the roof
            ?????
            profit"

    "question": "What are some of Richard's

    Here are bad examples:

    "question": "What happened on 11/23/2024?"
    "answer": "Bentley's Belated Birthday party"

    bad: uses a date in the question
    
    Here is the conversation:
    {conversation}
    """


class QuestionAnswerEntry(BaseModel):
    """A single evaluation entry with a question, answer, and referenced messages to be used later for evaluation."""
    question: str = Field(description="The question asked to be used for evaluation.")
    answer: str = Field(description="The answer to the question to be used for evaluation.")
    messages: List[str] = Field(description="The messages that were referenced to answer the question. These should include all info including username, content, and datetime")
    # message_summary: str = Field(description="A summary of the messages that were referenced to answer the question. Should be concise and informative. It can be a few sentences.")


class QuestionGenerator:

    def __init__(self, chat_db, llm=ChatOpenAI(model="gpt-4o"), chunk_size=100):
        self.chat_db = chat_db
        self.conversation_batches = self.chat_db.create_message_chunks(chunk_size)
        self.questions = []
        self.llm = llm.with_structured_output(QuestionAnswerEntry)

    def generate_questions(self, num_batches=10):
        for i in range(len(self.conversation_batches[:num_batches])):
            state = {
                "date": self.chat_db.get_last_date(),
                "conversation": self.conversation_batches[i]
            }
            prompt = ChatPromptTemplate.from_template(prompt_specific)
            chain = prompt | self.llm
            response = chain.invoke(state)
            self.questions.append(response.model_dump())
            print(response.model_dump())

        print(json.dumps(self.questions, indent=2))


    def save_questions(self, save_path):
        self.save_path = save_path
        with open(self.save_path, "w") as f:
            json.dump(self.questions, f, indent=2)