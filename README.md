Since this project is a sophisticated blend of medical AI, agentic workflows, and clinical interoperability, the README needs to speak to three different audiences: **Developers**, **Clinical Stakeholders**, and **Security/Compliance Officers**.

Here is a professional, comprehensive `README.md` for your repository.

***

# 🩺 TrialMatch AI: Agentic Clinical Trial Matchmaker

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/Powered%20By-LangGraph-green.svg)](https://github.com/langchain-ai/langgraph)

## 🌟 Overview
**TrialMatch AI** is an agentic system designed to automate the identification of eligible patients for clinical trials. Unlike traditional keyword search in Electronic Medical Records (EMRs), TrialMatch AI uses a **Reasoning-and-Verification loop** to parse unstructured medical documents, map them against complex trial criteria, and provide evidence-backed recommendations to physicians.

The system utilizes a **Human-in-the-Loop (HITL)** architecture, ensuring that no medical conclusion is finalized without physician oversight, while the agent handles the "heavy lifting" of document synthesis and gap analysis.

## 🚀 Core Features
- **Medical Doc Processing:** Extracts clinical entities (biomarkers, comorbidities, meds) from unstructured PDFs/HL7 documents.
- **Reasoning Engine:** Uses LangGraph to perform multi-step verification of trial inclusion/exclusion criteria.
- **Evidence-Based Citations:** Every match is backed by direct quotes and page references from the patient's medical record.
- **Physician-in-the-Loop:** A dedicated dashboard for doctors to approve, reject, or request deeper research from the agent.
- **Interoperability Ready:** Designed for integration via FHIR (Fast Healthcare Interoperability Resources) and SMART on FHIR.

## 🛠️ System Architecture
The system is built on a stateful graph:
1. **Matcher Node:** Performs an initial a-priori analysis of the patient vs. trial criteria.
2. **Verification Breakpoint:** The graph pauses, saving state to a checkpointer, and awaits physician input.
3. **Refinement Node:** If a physician requests more info, the agent re-queries the patient's longitudinal record to find specific missing data.
4. **Finalization:** Once approved, the match is pushed back to the EMR as a clinical observation.

## 📦 Installation

### Prerequisites
- Python 3.10 or higher
- OpenAI API Key (or Azure OpenAI endpoint)

### Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/trialmatch-ai.git
   cd trialmatch-ai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration:**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   # Optional: Azure configuration
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_KEY=your_key
   ```

## 🖥️ Running the Application

### 1. Launch the Physician Dashboard
The UI is built with Streamlit for rapid clinical prototyping.
```bash
streamlit run app.py
```

### 2. Testing the Backend (Headless)
You can run the state machine independently via the provided test script:
```bash
python tests/test_matchmaker.py
```

## 🛡️ Privacy & Security (HIPAA Compliance)
*This project is designed with a "Privacy First" mindset:*
- **PHI Scrubbing:** Implementation of a de-identification proxy to remove PII before sending data to LLMs.
- **State Persistence:** Use of encrypted checkpoints to store patient state.
- **Audit Trail:** Every state transition in LangGraph is logged, providing a full audit trail of how a match was determined.

## 🗺️ Roadmap
- [ ] **Phase 1:** Core Extraction & PDF Parsing (Complete)
- [ ] **Phase 2:** Reasoning Engine & LangGraph Logic (In Progress)
- [ ] **Phase 3:** Streamlit Physician Dashboard (In Progress)
- [ ] **Phase 4:** FHIR API Integration for Epic/Cerner
- [ ] **Phase 5:** Clinical Validation Study (Beta)

## 🤝 Contributing
We welcome contributions from the AI and Health-Tech community. Please fork the repo and create a PR for any feature requests or bug fixes.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
**Disclaimer:** *TrialMatch AI is a research prototype. It is not a certified medical device and should not be used for actual clinical decision-making without rigorous validation and regulatory approval (FDA/EMA).*