#  Aero-Scribe: Domain-Specialized AI Agent for Aviation MRO

**ET AI Hackathon 2026 - Phase 2 Submission**
**Target Problem Statement:** Problem Statement 5 (Domain-Specialized AI Agents with Compliance Guardrails)

##  Project Overview
The aviation Maintenance, Repair, and Overhaul (MRO) industry is facing a severe labor shortage and relies on fragmented, unstructured data. **Aero-Scribe** is an Agentic, Multimodal Maintenance Operating System designed to bridge the gap between the hangar floor and enterprise ERP systems.

It utilizes a multi-agent architecture to orchestrate complex troubleshooting workflows, handle multimodal edge cases, and operate strictly within regulatory compliance guardrails by generating an immutable audit trail.

##  Key Features & Agent Roles
1. **Diagnostic Agent (Multimodal):** Analyzes visual and acoustic data against technical manuals.
2. **Logistics Agent (ERP Connector):** Autonomously bridges the "Air Gap" by querying enterprise inventory systems to locate parts.
3. **Compliance Agent (Blockchain Guardrail):** Enforces strict regulatory compliance by generating a unique SHA-256 cryptographic hash securing a "Digital Twin" of the logbook.

##  Tech Stack
* **Frontend:** Python, Streamlit
* **AI Core:** Google Gemini 1.5 Flash (Multimodal)
* **Speech Synthesis:** gTTS (Neural Text-to-Speech)
* **Security:** Python `hashlib` (SHA-256 Cryptographic Hashing)

##  Local Setup Instructions
**1. Clone the repository**
`git clone https://github.com/YOUR_USERNAME/aero-scribe.git`
`cd aero-scribe`

**2. Install dependencies**
`pip install -r requirements.txt`

**3. Run the Application**
`streamlit run app.py`