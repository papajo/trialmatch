#This code implements the logic: Extract → Match → Interrupt for Human → Refine/Finalize.
import operator
from typing import Annotated, TypedDict, Dict, List, Union
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, BaseMessage

# --- 1. State Definition ---
class AgentState(TypedDict):
    patient_data: str            # Structured medical history
    trial_criteria: str          # Trial requirements
    match_analysis: str         # Agent's reasoning
    evidence_citations: List[str] # Page/Line references
    physician_feedback: str      # Input from UI
    status: str                  # "pending", "approved", "rejected", "refining"
    iterations: int

# --- 2. Node Implementations ---
llm = ChatOpenAI(model="gpt-4o", temperature=0)

def matcher_node(state: AgentState):
    """Analyzes patient data against trial criteria."""
    prompt = f"Patient: {state['patient_data']}\nTrial: {state['trial_criteria']}\nDetermine if the patient is eligible. Provide a detailed reasoning and a list of evidence quotes."
    response = llm.invoke(prompt)
    # In a real app, you'd use structured output (Pydantic) here
    return {
        "match_analysis": response.content,
        "status": "pending",
        "iterations": state.get("iterations", 0) + 1
    }

def research_refinement_node(state: AgentState):
    """Re-analyzes based on physician feedback."""
    prompt = f"Previous Analysis: {state['match_analysis']}\nPhysician Feedback: {state['physician_feedback']}\nPatient Data: {state['patient_data']}\nRe-evaluate the match based on the feedback."
    response = llm.invoke(prompt)
    return {
        "match_analysis": response.content,
        "status": "pending"
    }

# --- 3. Graph Construction ---
workflow = StateGraph(AgentState)

# Define Nodes
workflow.add_node("matchmaker", matcher_node)
workflow.add_node("refiner", research_refinement_node)

# Define Edges
workflow.set_entry_point("matchmaker")

# The "Human-in-the-loop" happens here via a conditional edge
def route_after_review(state: AgentState):
    if state["status"] == "approved":
        return END
    elif state["status"] == "rejected":
        return END
    else: # "refining"
        return "refiner"

workflow.add_conditional_edges(
    "matchmaker", 
    route_after_review, 
    {END: END, "refiner": "refiner"}
)

workflow.add_edge("refiner", "matchmaker") # Loop back for final check

# Memory for persistence (Checkpoints)
memory = MemorySaver()
app = workflow.compile(checkpointer=memory, interrupt_before=["matchmaker"]) 
# Note: In the real UI, we interrupt and wait for the physician's input.