from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
import json

from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# from utils import Evaluation, eval_msg

vector_store = Chroma(
    persist_directory="/Users/kastenwelsh/Documents/cse481-p/.data/vectorDB",
    collection_name="openai_0.0.3",
    embedding_function=OpenAIEmbeddings(),
)


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

    

# for question in questions:
#     state = {
#         "question": question.get("question"),
#         "ground_truth": question.get("answer"),
#         "ground_truth_supporting_messages": question.get("messages"),
#         "messages": [HumanMessage(content=question.get("question"))]
#     }

#     prompt = ChatPromptTemplate.from_template(sys_msg)

#     chain = prompt | llm

#     docs = retriever.invoke(question.get("question"))
#     print(docs)

#     model_answer = chain.invoke({'question': question.get("question"), 'documents':docs})

#     print(model_answer.content)

#     eval_prompt = ChatPromptTemplate.from_template(eval_msg)

#     eval_chain = eval_prompt | structured_llm

#     evaluation = eval_chain.invoke({"question": question.get("question"),
#                                     "model_response": model_answer.content, 
#                                     "ground_truth": question.get("answer"),
#                                     "ground_truth_supporting_messages": question.get("messages")})
    
#     print(evaluation.model_dump())


#     new_e = dict(evaluation)
#     new_e["question"] = question.get("question")
#     new_e["ground_truth"] = question.get("answer")
#     new_e["ground_truth_supporting_messages"] = question.get("messages")
#     evaluations.append(new_e)
#     print(json.dumps(new_e, indent=2))
        

# class Evaluation(BaseModel):
#     score: int = Field(..., description="The score given to the model's response")
#     reasoning: str = Field(..., description="The reasoning for the score")
#     model_answer: str = Field(..., description="The answer provided by the model")

# eval_msg = """
#     You are an agent designed to evaluate whether an answer to a prompt or question is correct or not.
#     You will be given a ground-truth answer with a set of corresponding messages, and the answer provided
#     by the model. Give a score 1-5 on how well the model answered the question.
#     1: The answer is completely incorrect or the model could not find any answer. For example, the answer is "I don't know."
#     or if the correct answer is "The sky is blue," the model's answer is "The sky is green."
#     2: The answer is vague and doesn't include any specific information. For example, the correct answer is "The sky is blue,"
#     but the model's answer is "The sky is a color."
#     3: The answer includes part of the correct information or references the correct information but is not complete.
#     For example, the correct answer is "The sky is blue and the grass is green," but the model's answer is "The sky is blue."
#     4: The answer is mostly correct but has some minor errors or omissions. It doesn't include anything wrong, 
#     but it doesn't include everything right. For example, the correct answer is "The sky is light blue,"
#     but the model's answer is "The sky is blue."
#     5: The answer is completely correct and includes all relevant information. No errors or omissions.
#     For example, the correct answer is "The sky is blue," and the model's answer is "The sky is blue."
#     Here is the question:
#     {question}
#     Here is the response provided by the model:
#     {model_response}
#     Here is the ground-truth answer:
#     {ground_truth}
#     Here are the ground_truth supporting messages:
#     {ground_truth_supporting_messages}
#     Provide reasoning for your score.
# """

# evaluations = []

# for question in questions:
#     state = {
#         "question": question.get("question"),
#         "ground_truth": question.get("answer"),
#         "ground_truth_supporting_messages": question.get("messages"),
#         "messages": [HumanMessage(content=question.get("question"))]
#     }

#     prompt = ChatPromptTemplate.from_template(sys_msg)

#     chain = prompt | llm

#     docs = retriever.invoke(question.get("question"))
#     print(docs)

#     model_answer = chain.invoke({'question': question.get("question"), 'documents':docs})

#     print(model_answer.content)

#     eval_prompt = ChatPromptTemplate.from_template(eval_msg)

#     eval_chain = eval_prompt | structured_llm

#     evaluation = eval_chain.invoke({"question": question.get("question"),
#                                     "model_response": model_answer.content, 
#                                     "ground_truth": question.get("answer"),
#                                     "ground_truth_supporting_messages": question.get("messages")})
    
#     print(evaluation.model_dump())


#     new_e = dict(evaluation)
#     new_e["question"] = question.get("question")
#     new_e["ground_truth"] = question.get("answer")
#     new_e["ground_truth_supporting_messages"] = question.get("messages")
#     evaluations.append(new_e)
#     print(json.dumps(new_e, indent=2))

# average_score = sum([e["score"] for e in evaluations]) / len(evaluations)

# print("Average Score:", average_score)

# try:
#     existing_evaluations = json.load(open("/Users/kastenwelsh/Documents/cse481-p/main/evaluations_discord1.json"))
# except FileNotFoundError:
#     existing_evaluations = []

# existing_evaluations.extend(evaluations)

# json.dump(existing_evaluations, open("/Users/kastenwelsh/Documents/cse481-p/main/evaluations_discord1.json", "w"), indent=2)


