from pydantic import BaseModel, Field
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langgraph.graph import MessagesState, START, StateGraph
from langchain.tools.retriever import create_retriever_tool
from langgraph.prebuilt import ToolNode
import operator
from typing import Annotated
import json

vector_store = Chroma(
    persist_directory="/Users/kastenwelsh/Documents/cse481-p/.data/vectorDB",
    collection_name="openai_0.0.2",
    embedding_function=OpenAIEmbeddings(),
)

class RetrievedDocState(MessagesState):
    question: str = Field(..., description="The question to evaluate")
    answer: str = Field(..., description="The answer to the question")
    context = Annotated[list, operator.add]
    step_back

class SubQueries(BaseModel):
    sub_queries: List[str] = Field(..., description="The subqueries generated from the original query")

retriever = vector_store.as_retriever(search_kwargs={"k": 1})

retriever_tool = create_retriever_tool(
    retriever,
    "retrieve_discord_messages",
    "Search and return relevant discord messages",
)

tools = [retriever_tool]

llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)

sys_msg = SystemMessage(content="""
    You an agent tasked with helping users recall information from a chat history.
    You have access to a tool to retrieve a small subset of messages from a discord
    chat history using embeddings. You can use this tool to help you answer user questions.""")

# https://github.com/NirDiamant/RAG_Techniques/blob/main/all_rag_techniques/query_transformations.ipynb
step_back_template = """You are an AI assistant tasked with generating broader, more general queries to improve context retrieval in a RAG system.
Given the original query, generate a step-back query that is more general and can help retrieve relevant background information.

Original query: {original_query}

Step-back query:"""

# https://github.com/NirDiamant/RAG_Techniques/blob/main/all_rag_techniques/query_transformations.ipynb
subquery_decomposition_template = """You are an AI assistant tasked with breaking down complex queries into simpler sub-queries for a RAG system.
Given the original query, decompose it into 2-4 simpler sub-queries that, when answered together, would provide a comprehensive response to the original query.

Original query: {original_query}

example: What are the impacts of climate change on the environment?

Sub-queries:
1. What are the impacts of climate change on biodiversity?
2. How does climate change affect the oceans?
3. What are the effects of climate change on agriculture?
4. What are the impacts of climate change on human health?"""

def original_query_agent(state: RetrievedDocState):
    res = [llm_with_tools.invoke([sys_msg] + state["messages"])]
    return {"messages": res}

def step_back_agent(state: RetrievedDocState):
    structured_llm = llm.with_structured_output(SubQueries)
    res = structured_llm.invoke([SystemMessage(content=step_back_template.format(original_query=state["question"]))])
    return {"messages": res}

def sub_query_agent(state: RetrievedDocState):
    structured_subquery_llm = llm.with_structured_output(SubQueries)
    structured_subquery_llm.bind_tools(tools)
    res = structured_subquery_llm.invoke()
    return {"messages": res}

def final_agent(state: RetrievedDocState):
    docs = state["sub_query_docs"] + state["step_back_docs"] + state["original_query_docs"]
    prompt = """
You are an AI assistant tasked with generating a final query to retrieve relevant information from a RAG system.
Given the retrieved documents from the original query, step-back query, and sub-queries, generate a final answer to the original query.

"""

def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return "evaluator"

builder = StateGraph(RetrievedDocState)

builder.add_node("original_query_agent", original_query_agent)
builder.add_node("step_back_agent", step_back_agent)
builder.add_node("sub_query_agent", sub_query_agent)
builder.add_node("final_agent", final_agent)
builder.add_node("tools", ToolNode(tools))

for node in ["original_query_agent", "step_back_agent", "sub_query_agent"]:
    builder.add_edge(START, node)
    builder.add_conditional_edges(node, should_continue, ["tools", "final_agent"])
    builder.add_edge("tools", node)

graph = builder.compile()

print(graph.get_graph().print_ascii())

# evaluations = []

# messages = graph.invoke(RetrievedDocState)

# for e in messages['evaluation']:
#     evaluations.append(e.model_dump())

# print(evaluations)

# json.dump(evaluations, open("/Users/kastenwelsh/Documents/cse481-p/newmain/answers.json", "w"), indent=2)
