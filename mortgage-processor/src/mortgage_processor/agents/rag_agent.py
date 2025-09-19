"""
Agentic RAG agent for mortgage knowledge retrieval
Uses LangGraph to build an intelligent retrieval system that decides when to search vs respond directly
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AIMessage

from ..rag_tools import (
    mortgage_retriever_tool,
    grade_mortgage_documents, 
    rewrite_mortgage_question
)
from ..utils.llm_factory import get_agent_llm, get_grader_llm


def create_mortgage_rag_agent():
    """
    Create an agentic RAG system for mortgage knowledge retrieval.
    
    This agent can:
    1. Decide whether to retrieve mortgage knowledge or respond directly
    2. Grade retrieved documents for relevance
    3. Rewrite questions if documents aren't relevant
    4. Generate informed responses using retrieved context
    """
    
    # Initialize the response model using centralized LLM factory
    response_model = get_agent_llm()
    
    def generate_query_or_respond(state: MessagesState):
        """
        Call the model to generate a response based on the current state.
        The LLM will decide to retrieve using the mortgage retriever tool, or respond directly.
        """
        system_prompt = """You are a helpful mortgage assistant. You have access to a mortgage knowledge retriever tool.

DECISION LOGIC:
- If the user asks about specific mortgage types, qualification requirements, loan processes, or technical mortgage details → USE the retrieve_mortgage_knowledge tool
- If the user asks general greetings, simple questions, or you already have sufficient knowledge → respond directly
- Always prioritize using retrieved information when it could provide more accurate or detailed mortgage guidance

When using tools, be sure to ask specific, focused questions to get the best retrieval results."""

        messages = [{"role": "system", "content": system_prompt}] + state["messages"]
        response = (
            response_model
            .bind_tools([mortgage_retriever_tool])
            .invoke(messages)
        )
        return {"messages": [response]}
    
    def grade_documents(state: MessagesState) -> Literal["generate_answer", "rewrite_question"]:
        """
        Determine whether the retrieved documents are relevant to the question.
        """
        # Get the original question
        question = state["messages"][0].content
        
        # Get the tool response (last message should be the tool result)
        tool_message = None
        for msg in reversed(state["messages"]):
            if hasattr(msg, 'type') and msg.type == 'tool':
                tool_message = msg
                break
        
        if not tool_message:
            # If no tool message found, generate answer anyway
            return "generate_answer"
        
        context = tool_message.content
        
        # Use the grading tool
        grade_result = grade_mortgage_documents.invoke({
            "question": question,
            "context": context
        })
        
        if grade_result == "relevant":
            return "generate_answer"
        else:
            return "rewrite_question"
    
    def rewrite_question(state: MessagesState):
        """
        Rewrite the original user question to improve retrieval results.
        """
        messages = state["messages"]
        original_question = messages[0].content
        
        # Use the rewriting tool
        improved_question = rewrite_mortgage_question.invoke({
            "question": original_question
        })
        
        # Replace the first message with the improved question
        return {"messages": [{"role": "user", "content": improved_question}]}
    
    def generate_answer(state: MessagesState):
        """
        Generate a final answer using the retrieved mortgage knowledge.
        """
        # Get the original question
        question = state["messages"][0].content
        
        # Get the retrieved context from tool message
        tool_message = None
        for msg in reversed(state["messages"]):
            if hasattr(msg, 'type') and msg.type == 'tool':
                tool_message = msg
                break
        
        if tool_message:
            context = tool_message.content
            prompt = f"""You are a knowledgeable mortgage assistant. Use the following retrieved information to answer the user's question accurately and helpfully.

Question: {question}

Retrieved Information: {context}

Instructions:
- Use the retrieved information as your primary source
- If the retrieved information doesn't fully answer the question, supplement with your general mortgage knowledge
- Be specific and helpful
- Use a friendly, professional tone
- Keep responses concise but informative (2-4 sentences)

Answer:"""
        else:
            prompt = f"""You are a knowledgeable mortgage assistant. Answer the following question using your general mortgage knowledge:

Question: {question}

Instructions:
- Be specific and helpful  
- Use a friendly, professional tone
- Keep responses concise but informative (2-4 sentences)

Answer:"""
        
        # Use the same centralized LLM for answer generation
        answer_model = get_agent_llm()
        response = answer_model.invoke([{"role": "user", "content": prompt}])
        return {"messages": [response]}
    
    # Build the workflow
    workflow = StateGraph(MessagesState)
    
    # Add nodes
    workflow.add_node("generate_query_or_respond", generate_query_or_respond)
    workflow.add_node("retrieve", ToolNode([mortgage_retriever_tool]))
    workflow.add_node("rewrite_question", rewrite_question) 
    workflow.add_node("generate_answer", generate_answer)
    
    # Add edges
    workflow.add_edge(START, "generate_query_or_respond")
    
    # Decide whether to retrieve or respond directly
    workflow.add_conditional_edges(
        "generate_query_or_respond",
        tools_condition,  # Uses built-in LangGraph condition
        {
            "tools": "retrieve",  # If LLM called tools, go to retrieve
            END: END,  # If no tools called, end (direct response)
        },
    )
    
    # After retrieval, grade the documents
    workflow.add_conditional_edges(
        "retrieve",
        grade_documents,
        {
            "generate_answer": "generate_answer",
            "rewrite_question": "rewrite_question"
        }
    )
    
    # After generating answer, end
    workflow.add_edge("generate_answer", END)
    
    # After rewriting question, try generating query/response again
    workflow.add_edge("rewrite_question", "generate_query_or_respond")
    
    # Compile the agent
    agent = workflow.compile()
    # agent.name = "mortgage_rag_agent"  # Not supported by create_react_agent
    
    return agent


# Create and export the RAG agent
mortgage_rag_agent = create_mortgage_rag_agent()

__all__ = ["create_mortgage_rag_agent", "mortgage_rag_agent"]
