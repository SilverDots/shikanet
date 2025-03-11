from typing import List
from pydantic import BaseModel, Field

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