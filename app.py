import streamlit as st
import requests
import time
import json

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Agentic Physics Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🤖 Agentic Physics Assistant")
st.markdown("A fully agentic, LLM-powered physics problem solver with memory, reflection, and learning.")

# Sidebar: Agent Status and Memory
def show_agent_status():
    st.sidebar.header("Agent Status")
    try:
        resp = requests.get(f"{API_URL}/health")
        if resp.ok:
            status = resp.json()
            st.sidebar.success("Agent is healthy!")
            st.sidebar.write(f"**Time:** {status['timestamp']}")
        else:
            st.sidebar.error("Agent not available.")
    except Exception:
        st.sidebar.error("Agent not available.")

    st.sidebar.header("Agent Memory")
    if st.sidebar.button("Show Recent Memory"):
        try:
            mem = requests.get(f"{API_URL}/agent_memory?limit=5").json()
            for exp in mem.get("experiences", []):
                st.sidebar.write(f"- {exp['problem_text'][:60]}...")
        except Exception:
            st.sidebar.warning("Could not fetch memory.")

    st.sidebar.header("Agent Knowledge")
    if st.sidebar.button("Show Knowledge (Pendulum)"):
        try:
            know = requests.get(f"{API_URL}/knowledge/pendulum").json()
            st.sidebar.write(know.get("knowledge", {}))
        except Exception:
            st.sidebar.warning("Could not fetch knowledge.")

show_agent_status()

# Main UI
st.markdown("## 📝 Enter a Physics Problem")
problem_text = st.text_area(
    "Physics Problem:",
    placeholder="e.g., A ball is thrown at 20 m/s at 45 degrees. What is its range?",
    height=100
)

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("🚀 Solve Problem", type="primary"):
        if not problem_text.strip():
            st.warning("Please enter a problem.")
        else:
            with st.spinner("Submitting to agent..."):
                resp = requests.post(f"{API_URL}/solve_problem", json={"problem_text": problem_text})
                if not resp.ok:
                    st.error("Agent backend error.")
                else:
                    task_id = resp.json()["task_id"]
                    st.info(f"Task ID: {task_id}")
                    # Poll for result
                    for _ in range(60):
                        time.sleep(1)
                        status = requests.get(f"{API_URL}/task_status/{task_id}").json()
                        if status["status"] == "completed":
                            result = status["result"]
                            st.success("**Agent Answer:**")
                            st.write(result.get("response", result))
                            # Reflection (if available)
                            if "reflection" in result:
                                st.info(f"**Agent Reflection:** {result['reflection']}")
                            break
                        else:
                            st.write("Waiting for agent...")
                    else:
                        st.warning("Timeout waiting for agent result.")

with col2:
    st.markdown("### 🎯 Set Agent Goal")
    goal = st.text_input("Set a new goal for the agent:", "Master projectile motion problems")
    if st.button("Set Goal"):
        try:
            resp = requests.post(f"{API_URL}/set_goal", params={"goal_description": goal})
            if resp.ok:
                st.success("Goal set!")
            else:
                st.error("Failed to set goal.")
        except Exception:
            st.error("Agent backend not available.")

    st.markdown("### 📚 Agent Knowledge Lookup")
    concept = st.text_input("Physics concept (e.g. pendulum, projectile_motion):", "projectile_motion")
    if st.button("Lookup Knowledge"):
        try:
            know = requests.get(f"{API_URL}/knowledge/{concept}").json()
            st.write(know.get("knowledge", {}))
        except Exception:
            st.warning("Could not fetch knowledge.")

st.markdown("---")
st.caption("Built with LangChain, ChromaDB, FastAPI, Celery, and OpenAI. Agentic, persistent, and self-improving.") 