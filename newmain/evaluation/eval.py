from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
import json

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# from utils import Evaluation, eval_msg


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
    by the model. Give a score 1-3 on how well the model answered the question.
    1: The answer is incorrect or the model could not find any answer.
    2: The answer is partially correct but has some errors or omissions.
    3: The answer is completely correct and includes all relevant information. No errors or omissions.
    Note: If the model response gives more information than required, that is acceptable as long as the additional information is not incorrect.

    Examples:

    question: "When is Bentley's Belated Birthday party?"
    model_response: "On the 23rd, at 8pm. There will be cake and ice cream."
    ground_truth: "On the 23rd"
    ground_truth_supporting_messages: ["Bentley's Belated Birthday party is on the 23rd"]

    score: 3
    reasoning: The model response is correct and includes all relevant information. The additional information about cake and ice cream is not incorrect.

    question: "What was Kasten’s game plan for 12/19/2024?"
    model_response: "nap until 8pm. do some work. go to the roof and watch the sunset."
    ground_truth: "nap until 8pm"
    ground_truth_supporting_messages: ["Kasten's game plan for 12/19/2024 was to nap until 8pm"]

    score: 3
    reasoning: The model response is correct and includes all relevant information. The additional information about doing some work and watching the sunset is not incorrect.

    question: "What is Richard's favorite color?"
    model_response: "Richard likes shades of bluish-green."
    ground_truth: "red"
    ground_truth_supporting_messages: ["Richard's favorite color is red."]

    score: 1
    reasoning: The model response is incorrect. Richard's favorite color is red, not shades of bluish-green.

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

class Evaluator:

    def __init__(self, 
                 model_responses,
                 question_data,
                 llm = ChatOpenAI(model="gpt-4o")):
        self.questions = question_data
        self.model_responses = model_responses
        self.llm = llm
        self.structured_llm = self.llm.with_structured_output(Evaluation)
        self.evaluations = []

    def evaluate(self):
        if len(self.questions) != len(self.model_responses):
            raise ValueError("Number of questions and model responses must be equal")
        for question, model_response in zip(self.questions, self.model_responses):
            state = {
                        "question": question.get("question"),
                        "model_response": model_response, 
                        "ground_truth": question.get("answer"),
                        "ground_truth_supporting_messages": question.get("messages")
                    }
            eval_prompt = ChatPromptTemplate.from_template(eval_msg)
            eval_chain = eval_prompt | self.structured_llm

            evaluation = eval_chain.invoke(state)
            
            print(evaluation.model_dump())

            new_e = dict(evaluation)
            new_e["question"] = question.get("question")
            new_e["ground_truth"] = question.get("answer")
            new_e["ground_truth_supporting_messages"] = question.get("messages")
            self.evaluations.append(new_e)
            print(json.dumps(new_e, indent=2))

    def average_score(self):
        return sum([e["score"] for e in self.evaluations]) / len(self.evaluations)

    def save_evaluations(self, file_path):
        try:
            existing_evaluations = json.load(open(file_path))
        except FileNotFoundError:
            existing_evaluations = []
        existing_evaluations.extend(self.evaluations)
        with open(file_path, "w") as f:
            json.dump(existing_evaluations, f, indent=2)