import streamlit as st
import random
import os
from openai import OpenAI

# Page Config for Mobile Optimization
st.set_page_config(
    page_title="Interpretation of Statutes - Courtroom Simulator",
    page_icon="⚖️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize OpenAI Client securely from Streamlit Secrets
api_key = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ OpenAI API Key missing! Please configure it in Streamlit Cloud Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# Course Syllabus Knowledge Base Context
SYLLABUS_CONTEXT = """
Interpretive Canons & Landmark Cases:
1. Always Speaking Statute / Dynamic Construction (Senior Electric Inspector v. Laxminarayan Chopra)
2. Mischief Rule / Purposive Approach (Heydon's Case, Smith v. Hughes, Bengal Immunity)
3. Golden Rule / Preventing Futility (R. v. Allen, Lee v. Knapp)
4. Literal Rule / Plain Meaning (Crawford v. Spooner, Sussex Peerage)
5. Noscitur a Sociis & Ejusdem Generis (CIT v. Bharti Cellular, Powell v. Kempton Park)
6. Non-Obstante Clauses & Ouster Clauses (Aswini Kumar Ghose, Dhulabhai, Anisminic)
7. Beneficial Construction (B. Shah v. Presiding Officer, Alembic Chemical Works)
8. Mandatory vs Directory Rules (Lalita Kumari, State of UP v. Babu Ram Upadhya)
"""

# Initialize Session States
if "messages" not in st.session_state:
    st.session_state.messages = []
if "scenario" not in st.session_state:
    st.session_state.scenario = None
if "round_count" not in st.session_state:
    st.session_state.round_count = 1

def generate_scenario():
    """Generates a novel real-world factual scenario based on the syllabus."""
    prompt = f"""
    You are a law professor. Based on this course context:
    {SYLLABUS_CONTEXT}
    
    Select ONE random canon/principle and generate a novel, modern real-world legal problem scenario. 
    Make it modern (e.g., involving AI, crypto, drones, or gig economy).
    Output format:
    ---
    **STATUTORY PROVISION AT ISSUE:** [Provide a short fictional statutory clause]
    **FACTUAL SCENARIO:** [Describe the facts of the dispute]
    **LEGAL ISSUE:** [Frame the main statutory dispute]
    ---
    Do NOT state which canon or precedent inspired this.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85
    )
    return response.choices[0].message.content

# Header & UI Title
st.title("⚖️ Courtroom Simulator")
st.caption("Interpretation of Statutes — Interactive Moot Court")

# Generate New Case Button
if st.button("🔄 Generate New Case Scenario", use_container_width=True):
    with st.spinner("Preparing courtroom scenario..."):
        st.session_state.scenario = generate_scenario()
        st.session_state.messages = []
        st.session_state.round_count = 1
    st.rerun()

# Display Case Scenario
if st.session_state.scenario:
    st.info(st.session_state.scenario)
else:
    st.info("Tap 'Generate New Case Scenario' above to start your courtroom session!")
    st.stop()

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Argument Input
if user_input := st.chat_input("State your argument (Counsel for Petitioner)..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Opposing Counsel Response
    lawyer_prompt = f"""
    You are the opposing Senior Advocate in court arguing against the student.
    SCENARIO & CONTEXT:
    {st.session_state.scenario}

    TRANSCRIPT SO FAR:
    {st.session_state.messages}

    Counter the student's argument forcefully using statutory principles, logic, and policy arguments. 
    Keep your response concise (under 120 words) and direct.
    """
    with st.chat_message("assistant"):
        with st.spinner("Opposing Counsel is formulating rebuttal..."):
            lawyer_res = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": lawyer_prompt}],
                temperature=0.7
            ).choices[0].message.content
            st.markdown(f"**Opposing Counsel:** {lawyer_res}")
            st.session_state.messages.append({"role": "assistant", "content": f"**Opposing Counsel:** {lawyer_res}"})
    
    st.session_state.round_count += 1

# Judge Ruling Button
st.divider()
if st.button("⚖️ Request Judicial Verdict & Grading", type="primary", use_container_width=True):
    if len(st.session_state.messages) < 2:
        st.warning("Please submit at least one argument before asking for the verdict!")
    else:
        judge_prompt = f"""
        You are a Supreme Court Judge evaluating a statutory interpretation argument.
        
        FULL CASE TRANSCRIPT:
        {st.session_state.messages}
        
        REFERENCE SYLLABUS CANONS:
        {SYLLABUS_CONTEXT}
        
        Provide your judgment in the following structure:
        1. **EVALUATION MATRIX**:
           - Canon Identification & Application (Score /10)
           - Logical & Statutory Reasoning (Score /10)
           - Distinguishing Fact vs. Law (Score /10)
        2. **RATIO DECIDENDI**: Explain the core principle that decides this case.
        3. **FINAL VERDICT**: State whether the Student or Opposing Counsel wins.
        """
        with st.spinner("The Judge is deliberating..."):
            judgment = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": judge_prompt}],
                temperature=0.3
            ).choices[0].message.content
            st.success("### 📜 Final Judicial Verdict")
            st.markdown(judgment)
