import uuid
from typing import List, Optional
from typing import TypedDict

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI 

from trustcall import create_extractor

import pandas as pd

import json
import os


# from utils import prompt_specific, QuestionAnswerEntry

from typing import List
from pydantic import BaseModel, Field

# from utils import prompt_specific, QuestionAnswerEntry

prompt_specific = """
    Create a list of questions and answers from the following conversation.
    These should be pointed questions with a single answer that can be found directly from the chat.
    Give a mix of who, what, when, where, why, and how questions as applicable.
    Explictly include dates, times and names in the question if needed rather than using pronouns or relative terms.

    Here are good example questions:


    "question": "When is Bentley's Belated Birthday party?",
    "answer": "On the 23rd",

    "question": "Did Nahum ever start reading Golden Kamuy in January?"
    "answer": "No"

    "question": "What was Kasten’s game plan for 12/19/2024?"
    "answer": "nap until 8pm
            get up and go to the roof
            ?????
            profit"

    Here are bad example questions:
    "question": "What is 'spidersnrhap' going to do after class?",
    "answer": "Build a CPU",

    issue: relative -- we don't when his class is

    "question": "Who is skipping a lecture tomorrow?",
    "answer": "silverdots"

    issue: relative -- we don't kno w when tomorrow is

    "question": "Where did dunsparce0p greet Richard?",
    "answer": "In the chat conversation."

    issue: too general -- we don't know when or what chat conversation and it's not specific enough
    
    Here is the conversation:
    {conversation}
    """


class QuestionAnswerEntry(BaseModel):
    """A single evaluation entry with a question, answer, and referenced messages to be used later for evaluation."""
    question: str = Field(description="The question asked to be used for evaluation.")
    answer: str = Field(description="The answer to the question to be used for evaluation.")
    messages: List[str] = Field(description="The messages that were referenced to answer the question. These should include all info including username, content, and datetime")


class QuestionGenerator:

    def __init__(self, chat_db, llm=ChatOpenAI(model="gpt-4o")):
        self.chat_db = chat_db
        self.conversation_batches = self.chat_db.create_message_chunks(chunk_size=50)
        self.questions = []
        self.llm = llm

    def generate_questions(self):
        user_extractor = create_extractor(
            self.llm,
            tools=[QuestionAnswerEntry],
            tool_choice="any",
            enable_inserts=True,
        )
        for i in range(len(self.conversation_batches[:1])):
            print("Generating questions for conversation batch", i)
            result = user_extractor.invoke(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt_specific.format(conversation=self.conversation_batches[i]),
                        }
                    ]
                }
            )

            for r, rmeta in zip(result["responses"], result["response_metadata"]):
                print(r.model_dump_json(indent=2))
                self.questions.append(r.model_dump())

        print(json.dumps(self.questions, indent=2))


    def save_questions(self, save_path):
        self.save_path = save_path
        with open(self.save_path, "w") as f:
            json.dump(self.questions, f, indent=2)





# FILE_PATH = f"/Users/kastenwelsh/Documents/cse481-p/.data/dataset/nvidia_page_{file_num}.csv"







# output_file = "/Users/kastenwelsh/Documents/cse481-p/newmain/questions_test.json"

# if os.path.exists(output_file):
#     with open(output_file, "r") as f:
#         existing_data = json.load(f)
# else:
#     existing_data = []

# existing_data.extend(data)

# with open(output_file, "w") as f:
#     json.dump(existing_data, f, indent=2)