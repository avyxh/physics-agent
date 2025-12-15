# app.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from PIL import Image
import pandas as pd
import requests
import json

# Import new agentic system
from agents.agentic_agent import PhysicsAgent
from utils.data_models import PhysicsProblem, Solution, VerificationResult, ProblemType
from config.settings import Config

# Configure Streamlit page
st.set_page_config(
    page_title="Physics AI Assistant (Agentic Enhanced)",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize agentic system
@st.cache_resource
def initialize_agentic_system():
    """Initialize the agentic system"""
    agent = PhysicsAgent()
    return agent

def solve_problem_agentic(problem_text, agent):
    """Solve problem using agentic system"""
    try:
        result = agent.solve_problem_autonomously(problem_text)
        return result
    except Exception as e:
        st.error(f"Error in agentic system: {str(e)}")
        return None

def display_agentic_status(agent):
    """Display the agentic system status in sidebar"""
    status = agent.get_agent_status()
    
    st.sidebar.markdown("## 🤖 Agentic Status")
    
    # Compact status display
    st.sidebar.metric("Experiences", status['total_experiences'])
    st.sidebar.metric("Knowledge", status['total_knowledge'])
    st.sidebar.metric("Strategies", status['total_strategies'])
    st.sidebar.metric("Active Goals", status['active_goals'])
    
    # Agent capabilities
    st.sidebar.markdown("### 🧠 Capabilities")
    for capability in status['capabilities']:
        st.sidebar.caption(f"• {capability.replace('_', ' ').title()}")
    
    # Current goals
    if status['current_goals']:
        st.sidebar.markdown("### 🎯 Current Goals")
        for goal in status['current_goals'][:2]:  # Show first 2 goals
            st.sidebar.caption(f"• {goal[:50]}...")

def display_solution(solution, verification):
    """Display solution with verification"""
    st.markdown("## 📊 Solution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"**Answer:** {solution.answer}")
        st.info(f"**Method:** {solution.method}")
        
        if solution.steps:
            st.markdown("**Steps:**")
            for i, step in enumerate(solution.steps, 1):
                st.markdown(f"{i}. {step}")
    
    with col2:
        st.metric("Confidence", f"{verification.confidence:.1%}")

        if verification.simulation_result:
            st.markdown("**Simulation Result:**")
            st.info(f"{verification.simulation_result}")

        if verification.agreement_score > 0:
            st.metric("Agreement", f"{verification.agreement_score:.1%}")
        
        if verification.error:
            st.error(f"**Verification Error:** {verification.error}")

def display_agentic_enhancement(result):
    """Display agentic enhancement as a small section"""
    if not result:
        return
    
    st.markdown("---")
    st.markdown("## 🤖 Agentic Enhancement")
    
    # Compact display of agentic action
    action_icons = {
        'autonomous_solving': '🧠',
        'exploration': '🔍', 
        'learning': '📖',
        'reflection': '🔄',
        'goal_setting': '🎯',
        'error': '❌'
    }
    
    action_icon = action_icons.get(result['action'], '🤖')
    st.info(f"{action_icon} **Agent Action:** {result['action'].replace('_', ' ').title()}")
    st.caption(f"🎯 {result['autonomous_decision']}")
    
    # Show brief result
    if result['action'] == 'autonomous_solving' and 'agent_response' in result:
        with st.expander("🧠 Agent Reasoning", expanded=True):
            st.markdown(result['agent_response'])
    
    if result['action'] == 'autonomous_solving' and 'reflection' in result:
        with st.expander("🔄 Agent Reflection", expanded=True):
            st.markdown(result['reflection'])
    
    elif result['action'] == 'exploration' and 'results' in result:
        with st.expander("🔍 Exploration Results", expanded=True):
            if not result['results']:
                st.markdown("The agent explored but didn't generate results.")
            for i, res in enumerate(result['results'][:2], 1):
                if 'result' in res and res['result']:
                    st.markdown(f"**Explored Question {i}:** `{res['question']}`")
                    if 'solution' in res['result']:
                        st.success(f"**Answer:** {res['result']['solution'].answer}")
                elif 'error' in res:
                    st.markdown(f"**Explored Question {i}:** `{res['question']}`")
                    st.warning(f"**Result:** Could not solve. The agent will learn from this failure.")

def display_solution_from_agent(agent_response: str):
    """Displays the comprehensive solution provided by the agent."""
    st.markdown("## 🤖 Agentic Solution")
    with st.expander("View Full Agent Response", expanded=True):
        st.markdown(agent_response)

# Main app
def main():
    st.title("🔬 Physics AI Assistant")
    st.markdown("**A truly agentic physics problem solver.**")
    
    agent = initialize_agentic_system()
    
    # --- Sidebar for Examples ---
    st.sidebar.title("🚀 Example Problems")
    st.sidebar.markdown("Click a button to load an example problem into the text area.")
    
    example_problems = {
        "Projectile": "A ball is thrown at 20 m/s at 45 degrees. What is its range?",
        "Collision": "Ball A (1 kg, 5 m/s) hits Ball B (1 kg, 0 m/s). What are the final velocities?",
        "Free Fall": "A stone falls from 15 meters. What is its final velocity?"
    }

    if st.sidebar.button("Projectile Motion"):
        st.session_state.problem_text = example_problems["Projectile"]
    if st.sidebar.button("Elastic Collision"):
        st.session_state.problem_text = example_problems["Collision"]
    if st.sidebar.button("Free Fall"):
        st.session_state.problem_text = example_problems["Free Fall"]
    
    # Initialize session state to hold the problem text
    if "problem_text" not in st.session_state:
        st.session_state.problem_text = ""

    # Main interface
    st.markdown("## 📝 Physics Problem Input")
    
    st.text_area(
        "Enter your physics problem below, or choose an example from the sidebar.",
        key="problem_text",  # Link this widget to the session state key
        placeholder="e.g., A ball is thrown at 20 m/s at a 45-degree angle. What is its range?",
        height=150
    )
    
    if st.button("🧠 Solve with Agent", type="primary"):
        if st.session_state.problem_text.strip(): # Read from session state
            with st.spinner("🤖 The agent is thinking... This may take a moment."):
                try:
                    # This is the new, simplified, agent-driven call
                    result = agent.run_agentic_pipeline(st.session_state.problem_text)
                    
                    if result and result["success"]:
                        # Display the agent's final, synthesized response
                        display_solution_from_agent(result["response"])
                    else:
                        st.error(f"The agent failed to produce a solution. Error: {result.get('response', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"A critical error occurred: {str(e)}")
        else:
            st.warning("Please enter a physics problem.")

if __name__ == "__main__":
    main() 