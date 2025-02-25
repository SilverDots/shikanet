from pydantic import BaseModel, Field
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import MessagesState, START, StateGraph
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import ToolNode
import json

vector_store = Chroma(
    persist_directory="/Users/kastenwelsh/Documents/cse481-p/.data/vectorDB",
    collection_name="openai_0.0.2",
    embedding_function=OpenAIEmbeddings(),
)

class Evaluation(BaseModel):
    score: int = Field(..., description="The score given to the model's response")
    reasoning: str = Field(..., description="The reasoning for the score")
    model_answer: str = Field(..., description="The answer provided by the model")

class EvalState(MessagesState):
    question: str = Field(..., description="The question to evaluate")
    ground_truth: str = Field(..., description="The ground truth answer")
    ground_truth_supporting_messages: List[str] = Field(..., description="The supporting messages for the ground truth answer")
    evaluation: Evaluation = Field(..., description="The evaluation of the model's response")

questions = json.load(open("/Users/kastenwelsh/Documents/cse481-p/newmain/questions_test.json"))

retriever = vector_store.as_retriever(search_kwargs={"k": 1})

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_discord_messages",
    "Search and return relevant discord messages",
)

tools = [retriever_tool]

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

structured_llm = llm.with_structured_output(Evaluation)

sys_msg = SystemMessage(content="""
    You an agent tasked with helping users recall information from a chat history.
    You have access to a tool to retrieve a small subset of messages from a discord
    chat history using embeddings. You can use this tool to help you answer user questions.""")

eval_msg = """
    You are an agent designed to evaluate whether an answer to a prompt or question is correct or not.
    You will be given a ground-truth answer with a set of corresponding messages, and the answer provided
    by the model. Give a score 1-10 on how well the model answered the question.
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

def agent(state: EvalState):
    res = [llm_with_tools.invoke([sys_msg] + state["messages"])]
    return {"messages": res}

def evaluator(state: EvalState):
    question = state["question"]
    model_response = state["messages"][-1].content
    ground_truth = state["ground_truth"]
    ground_truth_supporting_messages = state["ground_truth_supporting_messages"]
    
    eval_msg_formatted = eval_msg.format(
        question=question,
        model_response=model_response,
        ground_truth=ground_truth,
        ground_truth_supporting_messages=ground_truth_supporting_messages
    )

    res = [structured_llm.invoke([SystemMessage(content=eval_msg_formatted)] + state["messages"])]
    
    return {"evaluation": res}

def should_continue(state: EvalState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "evaluator"

builder = StateGraph(EvalState)

builder.add_node("agent", agent)
builder.add_node("evaluator", evaluator)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "agent")
builder.add_edge("tools", "agent")
builder.add_conditional_edges("agent", should_continue, ["tools", "evaluator"])

graph = builder.compile()

print(graph.get_graph().print_ascii())

evaluations = []

for question in questions[:20]:
    state = {
        "question": question.get("question"),
        "ground_truth": question.get("answer"),
        "ground_truth_supporting_messages": question.get("messages"),
        "messages": [HumanMessage(content=question.get("question"))]
    }

    messages = graph.invoke(state)

    for e in messages['evaluation']:
        print(question.get("question"))
        print(json.dumps(e.model_dump(), indent=2))
        new_e = dict(e)
        new_e["question"] = question.get("question")
        evaluations.append(new_e)

# take the average of the evaluation scores
average_score = sum([e["score"] for e in evaluations]) / len(evaluations)

try:
    existing_evaluations = json.load(open("/Users/kastenwelsh/Documents/cse481-p/newmain/evaluations.json"))
except FileNotFoundError:
    existing_evaluations = []

existing_evaluations.extend(evaluations)

json.dump(existing_evaluations, open("/Users/kastenwelsh/Documents/cse481-p/newmain/evaluations.json", "w"), indent=2)