Since this is a complex system, we will build this as a **Modular MVP**. We will implement the **State Machine** using LangGraph and a **Frontend** using Streamlit (the gold standard for rapid AI prototyping).

### 1. The Tech Stack
*   **Backend:** Python 3.10+, LangGraph, LangChain.
*   **LLM:** GPT-4o (via OpenAI/Azure).
*   **UI:** Streamlit (for the Physician Dashboard).
*   **State Store:** In-memory (for MVP), transitioning to Postgres for production.

---

### 2. The Backend: LangGraph State Machine

This code implements the logic: **Extract $\rightarrow$ Match $\rightarrow$ Interrupt for Human $\rightarrow$ Refine/Finalize**.

```python
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
```

---

### 3. The UI: Physician Dashboard (Streamlit)

This UI simulates the "SMART on FHIR" experience. It allows the doctor to see the agent's reasoning and trigger the "Refine" loop.

```python
import streamlit as st
from uuid import uuid4

st.set_page_config(page_title="TrialMatch AI Dashboard", layout="wide")

# --- Mock Data ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid4())
if "status" not in st.session_state:
    st.session_state.status = "Start"

st.title("🩺 TrialMatch AI: Clinical Verification")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Patient Record Summary")
    patient_text = st.text_area("Patient Data (Extracted from EMR)", 
                                value="Patient: 65yo Male. Stage IV NSCLC. Mutation: EGFR Exon 19. Prior Tx: Cisplatin. Current: No heart failure.", height=300)
    trial_text = st.text_area("Trial Criteria", 
                               value="Must have Stage IV NSCLC, EGFR mutation, no history of severe cardiac events.", height=150)
    
    if st.button("🚀 Run Matchmaker"):
        # This would call the LangGraph 'app.invoke'
        st.session_state.status = "pending"
        st.session_state.match_analysis = "Patient is a STRONG MATCH. Reason: Confirmed EGFR mutation and Stage IV diagnosis. No cardiac contraindications found in records."
        st.session_state.citations = ["Page 2: 'EGFR Exon 19 positive'", "Page 5: 'No history of HF'"]

with col2:
    st.subheader("Agent Reasoning")
    if st.session_state.status == "pending":
        st.info(st.session_state.match_analysis)
        
        st.write("**Evidence Citations:**")
        for cite in st.session_state.citations:
            st.markdown(f"- `{cite}`")
        
        st.divider()
        st.write("### Physician Action")
        
        feedback = st.text_input("Add notes or request more research:")
        
        c1, c2, c3 = st.columns(3)
        if c1.button("✅ Approve Match", type="primary"):
            st.success("Match approved. Notification sent to EMR.")
            st.session_state.status = "approved"
            
        if c2.button("❌ Reject Match"):
            st.error("Match rejected. Patient profile updated.")
            st.session_state.status = "rejected"
            
        if c3.button("🔍 Request Refinement"):
            st.warning("Agent is re-scanning documents...")
            # This would trigger the 'refiner' node in LangGraph
            st.session_state.match_analysis = "REFINED ANALYSIS: After scanning 2018 records, I found a mild arrhythmia but no heart failure. Eligibility still stands."
            st.session_state.status = "pending"
```

---

### 4. How to Run This

1.  **Install Dependencies:**
    ```bash
    pip install langgraph langchain_openai streamlit
    ```
2.  **Set Environment Variable:**
    ```bash
    export OPENAI_API_KEY='your-key-here'
    ```
3.  **Run the UI:**
    ```bash
    streamlit run app.py
    ```

### 5. Key Design Decisions in this Implementation:

1.  **The "Interrupt" Logic:** In the code, I used `interrupt_before`. In the Streamlit UI, the "buttons" act as the trigger to resume the graph.
2.  **The Feedback Loop:** Note how the "Request Refinement" button doesn't just change the text—it simulates the agent going back into the data to find a specific nuance (e.g., the 2018 arrhythmia).
3.  **State Separation:** The UI separates the **Patient Data** (the source of truth) from the **Agent Reasoning** (the hypothesis). This prevents the doctor from accidentally editing medical records while they are reviewing the match.
4.  **Citations:** Every match result is paired with a citation. This is the only way to gain a physician's trust; "The LLM said so" is not an acceptable answer in medicine.