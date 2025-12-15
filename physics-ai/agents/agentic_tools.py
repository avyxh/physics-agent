"""
LangChain Tools for the Agentic Physics System
"""
from langchain.tools import tool
from core.problem_parser import ProblemParser
from core.physics_solver import PhysicsSolver
from core.verification import VerificationEngine
from agents.agentic_memory import AgenticMemory
from utils.data_models import Solution
import requests

@tool
def solve_physics_problem(problem_text: str) -> str:
    """Solve a physics problem using analytical methods."""
    parser = ProblemParser()
    solver = PhysicsSolver()
    parsed = parser.parse_text_problem(problem_text)
    solution = solver.solve_problem(parsed)
    return f"Answer: {solution.answer} {solution.unit}\nMethod: {solution.method}\nSteps: {'; '.join(solution.steps)}"

@tool
def get_physics_knowledge(concept: str) -> str:
    """Retrieve knowledge about a physics concept from memory."""
    memory = AgenticMemory()
    knowledge = memory.get_knowledge(concept)
    if knowledge:
        return f"Concept: {knowledge['concept']}\nDescription: {knowledge['description']}\nFormulas: {', '.join(knowledge['formulas'])}\nExamples: {', '.join(knowledge['examples'])}"
    else:
        return f"No knowledge found for concept: {concept}"

@tool
def verify_solution_with_simulation(problem_text: str, analytical_solution: str) -> str:
    """
    Verifies a given analytical solution by running a physics simulation.
    Use this tool to gain confidence in an answer you have already found.
    Returns a structured report indicating success or failure and includes a confidence score.
    """
    try:
        parser = ProblemParser()
        problem = parser.parse_text_problem(problem_text)

        # Robustly extract the numerical answer from the solution string
        answer_str = analytical_solution
        if "Answer:" in answer_str:
            answer_str = answer_str.split("Answer:")[1].strip()

        unit = ""
        if '[' in answer_str:
            # Handles list-based answers like in collision problems
            answer_val = [float(x) for x in answer_str.split('[')[1].split(']')[0].split(',')]
            unit_part = answer_str.split(']')[1]
            if unit_part:
                unit = unit_part.strip()
        else:
            # Handles single numerical answers
            parts = answer_str.split()
            answer_val = float(parts[0])
            if len(parts) > 1:
                unit = parts[1]

        # Create a temporary Solution object for verification, now with the unit
        solution = Solution(answer=answer_val, method="analytical", unit=unit, steps=[])

        verifier = VerificationEngine()
        verification_result = verifier.verify_solution(problem, solution)

        if verification_result.is_valid:
            status = "SUCCESS: The analytical solution matches the simulation."
        else:
            status = "FAILURE: The analytical solution does NOT match the simulation."

        report = (
            f"Verification Status: {status}\\n"
            f"Confidence Score: {verification_result.confidence:.2%}\\n"
            f"Analytical Answer Provided: {answer_str}\\n"
            f"Simulation Result: {verification_result.simulation_result}"
        )
        return report
    except Exception as e:
        return f"Verification Status: ERROR. Failed to run verification due to an error: {str(e)}"

@tool
def reflect_on_solution(problem_text: str, solution: str, success: bool) -> str:
    """Reflect on a solution and extract learning insights."""
    # In a real system, this would use an LLM chain
    return f"Reflection: Solved '{problem_text}' with solution '{solution}'. Success: {success}. Key learning: Always check units and formulas."

@tool
def web_search(query: str) -> str:
    """Search the web for physics facts using DuckDuckGo Instant Answer API."""
    try:
        resp = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json&no_redirect=1&no_html=1")
        if resp.ok:
            data = resp.json()
            if data.get("AbstractText"):
                return data["AbstractText"]
            elif data.get("Answer"):
                return data["Answer"]
            elif data.get("RelatedTopics"):
                return data["RelatedTopics"][0].get("Text", "No answer found.")
            else:
                return "No answer found."
        else:
            return "Web search failed."
    except Exception as e:
        return f"Web search error: {e}"

@tool
def set_agent_goal(goal: str) -> str:
    """Set a new autonomous goal for the agent."""
    memory = AgenticMemory()
    from datetime import datetime, timedelta
    goal_id = f"goal_{datetime.now().timestamp()}"
    target_date = (datetime.now() + timedelta(days=7)).isoformat()
    memory.add_knowledge(goal_id, goal, [], [f"autonomous goal, target: {target_date}"])
    return f"Goal set: {goal}" 