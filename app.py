#This UI simulates the "SMART on FHIR" experience. 
#It allows the doctor to see the agent's reasoning and trigger the "Refine" loop.
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