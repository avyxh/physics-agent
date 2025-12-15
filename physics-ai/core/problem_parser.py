# core/problem_parser.py
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
from config.settings import Config
from utils.data_models import PhysicsProblem, PhysicsObject, ProblemType, InputType

class ProblemParser:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
    def parse_text_problem(self, text: str) -> PhysicsProblem:
        """Parse any natural language physics problem into a structured PhysicsProblem"""
        try:
            # Use LLM to intelligently understand and classify the problem
            llm_result = self._get_llm_understanding(text)
            
            if not llm_result:
                raise ValueError("Failed to understand the physics problem")
            
            # Create the structured problem from LLM output
            return self._create_problem_from_llm(llm_result, text)
            
        except Exception as e:
            raise ValueError(f"Error parsing problem: {str(e)}")

    def _get_llm_understanding(self, text: str) -> dict:
        """Use LLM to intelligently understand and structure any physics problem"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are an expert physics problem analyzer. Your task is to understand ANY physics problem written in natural language and extract all relevant information.

IMPORTANT: Be flexible and intelligent. Don't rely on exact templates. Understand the physics concepts regardless of how they're described.

Problem Types to Recognize:
1. PROJECTILE_MOTION - anything thrown, launched, or moving in a parabolic path
2. FREE_FALL - anything falling, dropped, or moving under gravity only
3. COLLISION - any impact, collision, or interaction between objects
4. PENDULUM - swinging objects, simple harmonic motion
5. SPRING_MOTION - mass-spring systems, oscillations
6. KINEMATICS - general motion problems (velocity, acceleration, distance, time)
7. DYNAMICS - force, mass, acceleration relationships
8. ENERGY - kinetic, potential, work, conservation of energy
9. ROTATIONAL - angular motion, torque, moment of inertia
10. FLUID_MECHANICS - pressure, buoyancy, fluid flow

For each problem, extract:
- problem_type: The most specific type that applies
- parameters: ALL numerical values with their units
- quantity_asked: What the user wants to find
- objects: Any physical objects involved
- constraints: Any limitations or conditions

Be very flexible with language:
- "A ball is thrown" = projectile motion
- "Something falls" = free fall  
- "Two things collide" = collision
- "A pendulum swings" = pendulum motion
- "A spring oscillates" = spring motion
- "How fast" = velocity/speed
- "How far" = distance/range
- "How long" = time/duration
- "What's the period" = oscillation time

Handle different units and formats:
- 20 m/s, 20 meters per second, 20 meters/second
- 45°, 45 degrees, 0.785 radians
- 10 m, 10 meters, 32.8 feet

Return a JSON object with this structure:
{
    "problem_type": "TYPE",
    "parameters": {
        "param_name": value,
        "param_name": value
    },
    "quantity_asked": "what_to_find",
    "objects": [
        {
            "name": "object_name",
            "mass": value,
            "velocity": value,
            "position": value
        }
    ],
    "constraints": {
        "constraint_name": "constraint_value"
    },
    "units": {
        "param_name": "unit"
    }
}

Examples:

Input: "A projectile is launched with initial velocity 20 m/s at angle 45°"
Output: {
    "problem_type": "PROJECTILE_MOTION",
    "parameters": {
        "initial_velocity": 20,
        "angle": 45
    },
    "quantity_asked": "range",
    "objects": [],
    "constraints": {},
    "units": {
        "initial_velocity": "m/s",
        "angle": "degrees"
    }
}

Input: "A stone falls from 15 meters. What is its final velocity?"
Output: {
    "problem_type": "FREE_FALL",
    "parameters": {
        "height": 15
    },
    "quantity_asked": "final_velocity",
    "objects": [],
    "constraints": {},
    "units": {
        "height": "m"
    }
}

Input: "Ball A (1 kg, 5 m/s) hits Ball B (1 kg, 0 m/s). What are the final velocities?"
Output: {
    "problem_type": "COLLISION",
    "parameters": {
        "mass_a": 1,
        "mass_b": 1,
        "velocity_a": 5,
        "velocity_b": 0
    },
    "quantity_asked": "final_velocities",
    "objects": [
        {"name": "Ball A", "mass": 1, "velocity": 5},
        {"name": "Ball B", "mass": 1, "velocity": 0}
    ],
    "constraints": {},
    "units": {
        "mass_a": "kg",
        "mass_b": "kg", 
        "velocity_a": "m/s",
        "velocity_b": "m/s"
    }
}

Input: "A pendulum has length 2 meters. What is its period?"
Output: {
    "problem_type": "PENDULUM",
    "parameters": {
        "length": 2
    },
    "quantity_asked": "period",
    "objects": [],
    "constraints": {},
    "units": {
        "length": "m"
    }
}"""},
                    {"role": "user", "content": f"Analyze this physics problem: {text}"}
                ],
                temperature=0.1  # Low temperature for consistent parsing
            )
            
            result = json.loads(response.choices[0].message.content)
            print(f"[DEBUG] LLM parsed problem: {result}")
            return result
            
        except Exception as e:
            print(f"[DEBUG] LLM parsing failed: {str(e)}")
            return None

    def _create_problem_from_llm(self, structured_problem: Dict[str, Any], original_text: str) -> PhysicsProblem:
        """Create a PhysicsProblem from LLM's structured output"""
        try:
            # Map the LLM problem type to our ProblemType enum
            problem_type = self._map_problem_type(structured_problem['problem_type'])
            
            # Extract objects if any
            objects = self._extract_objects(structured_problem.get('objects', []))
            
            # Build initial conditions from parameters
            initial_conditions = structured_problem.get('parameters', {})
            initial_conditions['quantity_asked'] = structured_problem.get('quantity_asked', '')
            
            # Add constraints
            constraints = structured_problem.get('constraints', {})
            
            return PhysicsProblem(
                problem_text=original_text,
                problem_type=problem_type,
                objects=objects,
                initial_conditions=initial_conditions,
                constraints=constraints,
                question=f"What is the {structured_problem.get('quantity_asked', 'result')}?"
            )
            
        except Exception as e:
            raise ValueError(f"Error creating problem from LLM output: {str(e)}")

    def _extract_objects(self, llm_objects: List[Dict]) -> List[PhysicsObject]:
        """Convert LLM's object descriptions to PhysicsObject instances"""
        objects = []
        for obj in llm_objects:
            try:
                physics_obj_params = {
                    'name': obj.get('name', 'Unknown'),
                    'mass': obj.get('mass'),
                    'velocity': obj.get('velocity'),
                    'position': obj.get('position'),
                    'length': obj.get('length'),
                    'height': obj.get('height')
                }
                # Remove None values
                physics_obj_params = {k: v for k, v in physics_obj_params.items() if v is not None}
                
                physics_obj = PhysicsObject(**physics_obj_params)
                objects.append(physics_obj)
            except Exception as e:
                print(f"[DEBUG] Error creating object {obj}: {str(e)}")
                continue
        return objects

    def _map_problem_type(self, llm_type: str) -> ProblemType:
        """Map LLM problem type to our ProblemType enum"""
        type_mapping = {
            'PROJECTILE_MOTION': ProblemType.PROJECTILE,
            'FREE_FALL': ProblemType.FREE_FALL,
            'COLLISION': ProblemType.COLLISION,
            'PENDULUM': ProblemType.PENDULUM,
            'SPRING_MOTION': ProblemType.PENDULUM,  # Map to pendulum for now
            'KINEMATICS': ProblemType.PROJECTILE,   # Map to projectile for now
            'DYNAMICS': ProblemType.PROJECTILE,     # Map to projectile for now
            'ENERGY': ProblemType.FREE_FALL,        # Map to free fall for now
            'ROTATIONAL': ProblemType.PENDULUM,     # Map to pendulum for now
            'FLUID_MECHANICS': ProblemType.FREE_FALL # Map to free fall for now
        }
        
        mapped_type = type_mapping.get(llm_type.upper())
        if not mapped_type:
            # Default to projectile motion for unknown types
            print(f"[DEBUG] Unknown problem type '{llm_type}', defaulting to PROJECTILE")
            return ProblemType.PROJECTILE
            
        return mapped_type

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numbers from text (utility function)"""
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        return [float(num) for num in numbers]