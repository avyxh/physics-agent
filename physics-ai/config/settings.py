# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # LLM Configuration
    LLM_MODEL = "gpt-4"  # or "gpt-3.5-turbo" for faster/cheaper
    LLM_TEMPERATURE = 0.1
    LLM_MAX_TOKENS = 1000
    
    # Physics Constants
    GRAVITY = 9.81  # m/s^2
    AIR_DENSITY = 1.225  # kg/m^3
    
    # Simulation Settings
    SIMULATION_TIMESTEP = 0.01  # seconds
    MAX_SIMULATION_TIME = 100   # seconds
    
    # Confidence Thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.9
    MEDIUM_CONFIDENCE_THRESHOLD = 0.7
    
    # File Paths
    PHYSICS_KNOWLEDGE_PATH = "data/physics_knowledge.json"
    PROBLEM_EXAMPLES_PATH = "data/problem_examples.json"
    
    # Agent Configuration
    AGENT_MEMORY_PATH = "data/agent_memory"
    AGENT_MAX_ITERATIONS = 5
    AGENT_VERBOSE = True