"""
LangChain-based Agentic Physics Agent (Advanced)
"""
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from agents.agentic_tools import solve_physics_problem, get_physics_knowledge, reflect_on_solution, web_search, set_agent_goal, verify_solution_with_simulation
from agents.agentic_memory import AgenticMemory
from config.settings import Config

class PhysicsAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.LLM_MODEL,
            temperature=Config.LLM_TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.tools = [
            solve_physics_problem,
            get_physics_knowledge,
            reflect_on_solution,
            web_search,
            set_agent_goal,
            verify_solution_with_simulation
        ]
        self.agent_executor = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            memory=self.memory,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True,
        )
        self.db = AgenticMemory()

    def run_agentic_pipeline(self, problem_text: str) -> dict:
        """
        Runs the full, end-to-end agentic pipeline with self-correction.
        """
        try:
            prompt = f"""
            You are a highly intelligent, flexible physics expert agent and educator. Your goal is to solve ANY physics problem accurately AND provide a comprehensive, educational explanation that teaches the user the underlying physics concepts.

            IMPORTANT: Be flexible and intelligent. Don't rely on exact templates or rigid patterns. Understand the physics concepts regardless of how they're described.

            Here is your intelligent problem-solving approach:
            1.  **Understand**: First, analyze the problem to understand what physics concepts are involved. The problem could be about:
                - Projectile motion (anything thrown, launched, or moving in a parabolic path)
                - Free fall (anything falling, dropped, or moving under gravity only)
                - Collisions (any impact, collision, or interaction between objects)
                - Pendulum motion (swinging objects, simple harmonic motion)
                - Spring motion (mass-spring systems, oscillations)
                - General kinematics (velocity, acceleration, distance, time)
                - Dynamics (force, mass, acceleration relationships)
                - Energy (kinetic, potential, work, conservation of energy)
                - Rotational motion (angular motion, torque, moment of inertia)
                - Fluid mechanics (pressure, buoyancy, fluid flow)
                - Or any other physics concept

            2.  **Solve**: Use the 'solve_physics_problem' tool to get an initial, analytical solution. The tool is intelligent and can handle various problem types.

            3.  **Verify**: Use the 'verify_solution_with_simulation' tool to check if your analytical answer is correct by comparing it with a physics simulation.

            4.  **Analyze Results**: Look at the verification status:
                - If 'SUCCESS': Your solution is likely correct.
                - If 'FAILURE' or 'ERROR': Your initial solution may be wrong, or there might be a conceptual error.

            5.  **Self-Correction (if needed)**: If verification failed:
                - Use the `web_search` tool to research the correct formulas and concepts for this specific problem.
                - Try to understand why your initial approach was wrong.
                - Use `solve_physics_problem` again with your new understanding.
                - Verify the new solution.

            6.  **Synthesize Final Answer**: Provide a comprehensive, educational explanation that includes:
                
                **A. Problem Analysis**: 
                - What type of physics problem is this?
                - What concepts are involved?
                - What are the given parameters and what are we trying to find?
                
                **B. Physics Concepts**:
                - Explain the relevant physics principles (e.g., "For projectile motion, we use the range formula R = (v₀² sin 2θ) / g")
                - Why these formulas apply to this situation
                - Any assumptions being made
                
                **C. Step-by-Step Solution**:
                - Show the exact calculations with units
                - Break down each step clearly
                - Show intermediate results
                - Explain what each calculation represents
                
                **D. Verification Process**:
                - Explain how you verified the solution
                - Compare analytical vs simulation results
                - Discuss the confidence level and any discrepancies
                
                **E. Final Answer**:
                - State the final answer with proper units
                - Summarize the key physics concepts demonstrated
                
                **F. Learning Points** (if applicable):
                - If you had to self-correct, explain what you learned
                - Any important physics insights from this problem
                - Common mistakes to avoid

            Be flexible with language and problem types. Handle variations like:
            - "A ball is thrown" vs "A projectile is launched" vs "Something is fired"
            - "How fast" vs "What's the velocity" vs "Find the speed"
            - "How far" vs "What's the range" vs "Find the distance"
            - Different units and formats (m/s, meters per second, km/h, etc.)

            Remember: Your goal is not just to give the answer, but to TEACH the physics concepts and reasoning process.

            Begin solving this physics problem: "{problem_text}"
            """
            
            final_response = self.agent_executor.run(prompt)
            
            self.db.add_experience(problem_text, final_response, True, {"type": "self_correcting_pipeline"})
            
            return {
                "response": final_response,
                "success": True
            }

        except Exception as e:
            return {
                "response": f"The agent encountered a critical error: {str(e)}",
                "success": False
            }

    def solve_problem_autonomously(self, problem_text: str) -> dict:
        """Solve problem using agentic system with autonomous decision making"""
        try:
            # Use the agent to autonomously decide how to solve the problem
            response = self.agent_executor.run(f"Solve this physics problem autonomously: {problem_text}")
            
            # Add to memory
            self.db.add_experience(problem_text, response, True, {"type": "autonomous_solve"})
            
            return {
                "action": "autonomous_solving",
                "autonomous_decision": "Used LangChain agent to autonomously solve the problem",
                "agent_response": response,
                "success": True
            }
        except Exception as e:
            return {
                "action": "error",
                "autonomous_decision": f"Error in autonomous solving: {str(e)}",
                "success": False
            }

    def explore_physics_concept(self, concept: str) -> dict:
        """Explore a physics concept autonomously"""
        try:
            response = self.agent_executor.run(f"Explore and explain this physics concept: {concept}")
            return {
                "action": "exploration",
                "autonomous_decision": f"Explored concept: {concept}",
                "results": [{"question": f"What is {concept}?", "result": {"solution": {"answer": response}}}]
            }
        except Exception as e:
            return {
                "action": "error",
                "autonomous_decision": f"Error exploring concept: {str(e)}"
            }

    def learn_from_experience(self) -> dict:
        """Learn from past experiences"""
        try:
            # Get recent experiences
            recent_experiences = self.db.get_similar_experiences("physics problem", limit=3)
            if recent_experiences:
                reflection = self.agent_executor.run(f"Learn from these experiences: {recent_experiences}")
                return {
                    "action": "learning",
                    "autonomous_decision": "Analyzed past experiences to improve future performance",
                    "reflection": reflection
                }
            else:
                return {
                    "action": "learning",
                    "autonomous_decision": "No recent experiences to learn from",
                    "reflection": "No experiences available."
                }
        except Exception as e:
            return {
                "action": "error",
                "autonomous_decision": f"Error in learning: {str(e)}",
                "reflection": "No experiences available."
            }

    def set_autonomous_goal(self, goal: str) -> dict:
        """Set an autonomous goal"""
        try:
            result = self.agent_executor.run(f"Set and plan for this goal: {goal}")
            return {
                "action": "goal_setting",
                "autonomous_decision": f"Set goal: {goal}",
                "goal_result": result
            }
        except Exception as e:
            return {
                "action": "error",
                "autonomous_decision": f"Error setting goal: {str(e)}"
            }

    def get_agent_status(self) -> dict:
        """Get current agent status"""
        try:
            # Get memory statistics
            experiences = self.db.get_similar_experiences("", limit=1000)  # Get all
            knowledge_items = self.db.search_knowledge("", limit=1000)  # Get all
            
            return {
                "total_experiences": len(experiences),
                "total_knowledge": len(knowledge_items),
                "total_strategies": 5,  # Hardcoded for now
                "active_goals": 1,  # Hardcoded for now
                "capabilities": [
                    "autonomous_problem_solving",
                    "concept_exploration", 
                    "experience_learning",
                    "goal_setting",
                    "reflection"
                ],
                "current_goals": ["Master physics problem solving"]
            }
        except Exception as e:
            return {
                "total_experiences": 0,
                "total_knowledge": 0,
                "total_strategies": 0,
                "active_goals": 0,
                "capabilities": [],
                "current_goals": [],
                "error": str(e)
            }

    def solve_problem(self, problem_text: str) -> dict:
        # If the problem is complex, break it down
        if any(word in problem_text.lower() for word in ["and", "then", "after", "while", "simultaneously"]):
            subproblems = self._split_into_subproblems(problem_text)
            responses = []
            for sub in subproblems:
                resp = self.agent_executor.run(f"Solve this physics problem: {sub}")
                self.db.add_experience(sub, resp, True, {"type": "solve"})
                responses.append(resp)
            return {"response": responses, "note": "Solved as multiple subproblems."}
        else:
            response = self.agent_executor.run(f"Solve this physics problem: {problem_text}")
            self.db.add_experience(problem_text, response, True, {"type": "solve"})
            return {"response": response}

    def reflect(self, problem_text: str, solution: str, success: bool) -> dict:
        reflection = self.agent_executor.run(f"Reflect on this solution: Problem: {problem_text}, Solution: {solution}, Success: {success}")
        return {"reflection": reflection}

    def get_knowledge(self, concept: str) -> dict:
        return self.db.get_knowledge(concept)

    def set_goal(self, goal: str) -> dict:
        result = self.agent_executor.run(f"Set a new goal: {goal}")
        return {"result": result}

    def web_search(self, query: str) -> dict:
        result = self.agent_executor.run(f"Web search: {query}")
        return {"result": result}

    def _split_into_subproblems(self, problem_text: str):
        # Naive split: split on 'and', 'then', etc.
        import re
        return [s.strip() for s in re.split(r'and|then|after|while|simultaneously', problem_text) if s.strip()] 