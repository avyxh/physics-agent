# core/physics_solver.py
import sympy as sp
import numpy as np
from typing import Dict, Any, List
from utils.data_models import PhysicsProblem, Solution, ProblemType
from utils.physics_math import PhysicsMath
from config.settings import Config
import math
import openai
import json
import re

class PhysicsSolver:
    def __init__(self):
        self.client = openai.OpenAI()
        self.math_utils = PhysicsMath()
        
    def solve_problem(self, problem: PhysicsProblem) -> Solution:
        """Solve a physics problem"""
        try:
            print(f"Debug PhysicsSolver: Solving {problem.problem_type.value} problem")
            
            result = None
            if problem.problem_type == ProblemType.PROJECTILE:
                result = self._solve_projectile_motion(
                    problem.initial_conditions.get('initial_velocity', 0),
                    problem.initial_conditions.get('angle', 0),
                    problem.initial_conditions.get('height', 0)
                )
                if result:
                    quantity_asked = problem.initial_conditions.get('quantity_asked', 'range')
                    if quantity_asked == 'range':
                        result['answer'] = result['range']
                        result['unit'] = 'm'
                    elif quantity_asked == 'max_height':
                        result['answer'] = result['max_height']
                        result['unit'] = 'm'
                    elif quantity_asked == 'time_flight':
                        result['answer'] = result['time_flight']
                        result['unit'] = 's'
                    else:
                        result['answer'] = result['range']
                        result['unit'] = 'm'
                        
            elif problem.problem_type == ProblemType.FREE_FALL:
                result = self._solve_free_fall(problem)
                if result:
                    quantity_asked = problem.initial_conditions.get('quantity_asked', 'final_velocity')
                    if quantity_asked == 'final_velocity':
                        result['answer'] = result['final_velocity']
                        result['unit'] = 'm/s'
                    elif quantity_asked == 'distance':
                        result['answer'] = result['distance']
                        result['unit'] = 'm'
                    elif quantity_asked == 'time_fall':
                        result['answer'] = result['time_fall']
                        result['unit'] = 's'
                    else:
                        result['answer'] = result['final_velocity']
                        result['unit'] = 'm/s'
                        
            elif problem.problem_type == ProblemType.PENDULUM:
                result = self._solve_pendulum(
                    problem.initial_conditions.get('length', 0),
                    problem.initial_conditions.get('initial_angle', 30)
                )
                if result:
                    quantity_asked = problem.initial_conditions.get('quantity_asked', 'period')
                    if quantity_asked == 'max_velocity':
                        result['answer'] = result['max_velocity']
                        result['unit'] = 'm/s'
                    else:
                        result['answer'] = result['period']
                        result['unit'] = 's'
                        
            elif problem.problem_type == ProblemType.COLLISION:
                if len(problem.objects) >= 2:
                    result = self._solve_collision(
                        problem.objects[0].mass,
                        problem.objects[1].mass,
                        problem.objects[0].velocity,
                        problem.objects[1].velocity
                    )
                    # Collision solver now returns answer, unit, and steps directly
            
            if not result:
                raise ValueError("Could not solve problem")
            
            print(f"Debug PhysicsSolver: result={result}")
            
            # Create solution object
            solution = Solution(
                answer=result['answer'],
                unit=result['unit'],
                steps=result.get('steps', []),
                method='analytical',
                visualization_data=result
            )
            
            print(f"Debug PhysicsSolver: answer={solution.answer}, unit={solution.unit}")
            return solution
            
        except Exception as e:
            print(f"Debug PhysicsSolver: Error solving problem - {str(e)}")
            raise
    
    def _solve_kinematics(self, problem: PhysicsProblem) -> Solution:
        """Solve kinematics problems"""
        
        # Check if it's projectile motion
        if "projectile" in problem.problem_text.lower() or "thrown" in problem.problem_text.lower():
            return self._solve_projectile_motion(problem)
        
        # Check if it's free fall
        elif "drop" in problem.problem_text.lower() or "fall" in problem.problem_text.lower():
            return self._solve_free_fall(problem)
        
        else:
            return self._solve_general_kinematics(problem)
    
    def _solve_projectile_motion(self, initial_velocity: float, angle: float, height: float = 0) -> dict:
        """Solve projectile motion problem"""
        try:
            print(f"Debug PhysicsMath: v0={initial_velocity}, angle={angle}, height={height}")
            
            # Convert angle to radians
            angle_rad = math.radians(angle)
            
            # Calculate initial velocities
            v0x = initial_velocity * math.cos(angle_rad)
            v0y = initial_velocity * math.sin(angle_rad)
            print(f"Debug PhysicsMath: v0x={v0x}, v0y={v0y}")
            
            # Calculate time of flight
            # Using quadratic formula: h = h0 + v0y*t - 0.5*g*t^2
            # When h = 0: 0 = h0 + v0y*t - 0.5*g*t^2
            a = 0.5 * Config.GRAVITY  # Note: positive a since we're solving for h = 0
            b = -v0y  # Note: negative b since we're solving for h = 0
            c = -height  # Note: negative c since we're solving for h = 0
            
            discriminant = b**2 - 4*a*c
            print(f"Debug PhysicsMath: discriminant={discriminant}")
            
            if discriminant < 0:
                raise ValueError("No real solution for time of flight")
            
            # Use the positive root for time of flight
            time_flight = (-b + math.sqrt(discriminant)) / (2*a)
            if time_flight < 0:
                time_flight = (-b - math.sqrt(discriminant)) / (2*a)
            
            print(f"Debug PhysicsMath: time_flight={time_flight}")
            
            # Calculate range
            range_x = v0x * time_flight
            print(f"Debug PhysicsMath: range_x={range_x}")
            
            # Calculate maximum height
            # Time to reach max height: t = v0y/g
            time_to_max = v0y / Config.GRAVITY
            max_height = height + v0y * time_to_max - 0.5 * Config.GRAVITY * time_to_max**2
            
            # Calculate final velocity
            final_velocity_x = v0x
            final_velocity_y = v0y - Config.GRAVITY * time_flight
            final_velocity = math.sqrt(final_velocity_x**2 + final_velocity_y**2)
            
            result = {
                'range': range_x,
                'time_flight': time_flight,
                'max_height': max_height,
                'final_velocity': final_velocity,
                'final_velocity_x': final_velocity_x,
                'final_velocity_y': final_velocity_y,
                'initial_velocity': initial_velocity,
                'angle': angle,
                'height': height
            }
            
            print(f"Debug PhysicsMath: final result={result}")
            return result
            
        except Exception as e:
            print(f"Debug PhysicsMath: Error in projectile calculation - {str(e)}")
            return {'error': str(e)}
    
    def _solve_free_fall(self, problem: PhysicsProblem) -> Dict[str, Any]:
        """Solve free fall problem"""
        print("Debug PhysicsSolver: Solving free_fall problem")
        
        # Get parameters
        height = problem.initial_conditions.get('height', 0)
        initial_velocity = problem.initial_conditions.get('initial_velocity', 0)
        time = problem.initial_conditions.get('time', 0)
        quantity_asked = problem.initial_conditions.get('quantity_asked', 'final_velocity')
        
        print(f"Debug PhysicsSolver: Parameters - height={height}, initial_velocity={initial_velocity}, time={time}, quantity_asked={quantity_asked}")
        
        g = 9.81  # m/s^2
        
        try:
            if time > 0:
                # Time-based calculation
                distance = 0.5 * g * time * time
                final_velocity = g * time
                result = {
                    'distance': distance,
                    'final_velocity': final_velocity,
                    'time_fall': time,
                    'initial_velocity': initial_velocity,
                    'answer': distance if quantity_asked == 'distance' else final_velocity,
                    'unit': 'm' if quantity_asked == 'distance' else 'm/s'
                }
            else:
                # Height-based calculation
                final_velocity = math.sqrt(2 * g * height)
                time_fall = math.sqrt(2 * height / g)
                result = {
                    'distance': height,
                    'final_velocity': final_velocity,
                    'time_fall': time_fall,
                    'initial_velocity': initial_velocity,
                    'answer': final_velocity if quantity_asked == 'final_velocity' else height,
                    'unit': 'm/s' if quantity_asked == 'final_velocity' else 'm'
                }
            
            print(f"Debug PhysicsSolver: result={result}")
            print(f"Debug PhysicsSolver: answer={result['answer']}, unit={result['unit']}")
            return result
            
        except Exception as e:
            print(f"Debug PhysicsSolver: Error in free fall calculation - {str(e)}")
            return {'error': str(e)}
    
    def _solve_general_kinematics(self, problem: PhysicsProblem) -> Solution:
        """Solve general kinematics problems using symbolic math"""
        
        # Use sympy for symbolic solutions
        t, v0, a, s = sp.symbols('t v0 a s')
        
        # Standard kinematic equations
        equations = {
            'v = v0 + at': v0 + a*t,
            's = v0*t + (1/2)*a*t^2': v0*t + sp.Rational(1,2)*a*t**2,
            'v^2 = v0^2 + 2as': v0**2 + 2*a*s
        }
        
        steps = [
            "General kinematics problem",
            "Available equations:",
            "  v = v₀ + at",
            "  s = v₀t + ½at²", 
            "  v² = v₀² + 2as",
            "Need more specific information to solve numerically"
        ]
        
        return Solution(
            answer="Requires more specific information",
            method="general_kinematics",
            steps=steps,
            confidence=0.5,
            alternative_methods=["Provide specific values for calculation"]
        )
    
    def _solve_dynamics(self, problem: PhysicsProblem) -> Solution:
        """Solve dynamics problems (forces, Newton's laws)"""
        # Implementation for dynamics problems
        return Solution(
            answer="Dynamics solver not implemented yet",
            method="dynamics",
            steps=["Will implement dynamics solver"],
            confidence=0.0
        )
    
    def _solve_energy(self, problem: PhysicsProblem) -> Solution:
        """Solve energy problems"""
        # Implementation for energy problems
        return Solution(
            answer="Energy solver not implemented yet", 
            method="energy",
            steps=["Will implement energy solver"],
            confidence=0.0
        )
    
    def _solve_momentum(self, problem: PhysicsProblem) -> Solution:
        """Solve momentum problems"""
        # Implementation for momentum problems
        return Solution(
            answer="Momentum solver not implemented yet",
            method="momentum", 
            steps=["Will implement momentum solver"],
            confidence=0.0
        )
    
    def _solve_oscillations(self, problem: PhysicsProblem) -> Solution:
        """Solve oscillation problems (pendulum, springs)"""
        
        if "pendulum" in problem.problem_text.lower():
            return self._solve_pendulum(problem)
        
        return Solution(
            answer="Oscillation solver for non-pendulum not implemented yet",
            method="oscillations",
            steps=["Will implement other oscillation types"],
            confidence=0.0
        )
    
    def _solve_pendulum(self, length: float, initial_angle: float = 30) -> dict:
        """Solve pendulum problem"""
        try:
            if length <= 0:
                raise ValueError("Pendulum length must be a positive value.")

            # Using small angle approximation
            # T = 2π√(L/g)
            period = 2 * math.pi * math.sqrt(length / Config.GRAVITY)
            
            # Calculate maximum velocity
            # Using conservation of energy: mgh = 0.5mv^2
            # h = L(1 - cos(θ))
            height = length * (1 - math.cos(math.radians(initial_angle)))
            max_velocity = math.sqrt(2 * Config.GRAVITY * height)
            
            # Calculate frequency
            frequency = 1 / period if period > 0 else 0
            
            return {
                'period': period,
                'max_velocity': max_velocity,
                'frequency': frequency,
                'length': length,
                'initial_angle': initial_angle
            }
            
        except Exception as e:
            print(f"Debug PhysicsMath: Error in pendulum calculation - {str(e)}")
            raise e
    
    def _solve_general(self, problem: PhysicsProblem) -> Solution:
        """General solver for unclassified problems"""
        return Solution(
            answer="Problem type not recognized - please be more specific",
            method="general_fallback",
            steps=["Could not classify problem type", "Please provide more details"],
            confidence=0.1
        )

    def _solve_collision(self, mass_a: float, mass_b: float, velocity_a: float, velocity_b: float = 0) -> dict:
        """Solve elastic collision problem"""
        try:
            # Handle velocity_a if it's a list
            if isinstance(velocity_a, list):
                velocity_a = velocity_a[0]
            if isinstance(velocity_b, list):
                velocity_b = velocity_b[0]
            
            # Check for zero mass to avoid division by zero
            if mass_a <= 0 or mass_b <= 0:
                raise ValueError("Mass must be greater than zero")
            
            # Using conservation of momentum and energy for elastic collisions
            # v1f = ((m1-m2)v1i + 2m2v2i)/(m1+m2)
            # v2f = ((m2-m1)v2i + 2m1v1i)/(m1+m2)
            
            total_mass = mass_a + mass_b
            if total_mass <= 0:
                raise ValueError("Total mass must be greater than zero")
            
            velocity_a_final = ((mass_a - mass_b) * velocity_a + 2 * mass_b * velocity_b) / total_mass
            velocity_b_final = ((mass_b - mass_a) * velocity_b + 2 * mass_a * velocity_a) / total_mass
            
            print(f"Debug: Collision calculation - mass_a={mass_a}, mass_b={mass_b}, v_a={velocity_a}, v_b={velocity_b}")
            print(f"Debug: Results - v_a_final={velocity_a_final}, v_b_final={velocity_b_final}")
            
            # Format the steps without using f-strings with lists
            steps = [
                "1. Ball A mass: {} kg, initial velocity: {} m/s".format(mass_a, velocity_a),
                "2. Ball B mass: {} kg, initial velocity: {} m/s".format(mass_b, velocity_b),
                "3. Final velocity of Ball A: {:.2f} m/s".format(velocity_a_final),
                "4. Final velocity of Ball B: {:.2f} m/s".format(velocity_b_final)
            ]
            
            return {
                'velocity_a_final': velocity_a_final,
                'velocity_b_final': velocity_b_final,
                'mass_a': mass_a,
                'mass_b': mass_b,
                'velocity_a': velocity_a,
                'velocity_b': velocity_b,
                'answer': [velocity_a_final, velocity_b_final],
                'unit': 'm/s',
                'steps': steps
            }
            
        except Exception as e:
            print(f"Debug PhysicsMath: Error in collision calculation - {str(e)}")
            raise ValueError(f"Error in collision calculation: {str(e)}")

    def _generate_solution_steps(self, problem: PhysicsProblem, result: Dict[str, Any]) -> List[str]:
        """Generate step-by-step solution explanation"""
        steps = []
        
        if problem.problem_type == ProblemType.PROJECTILE:
            steps = [
                f"1. Initial velocity: {result['initial_velocity']} m/s",
                f"2. Launch angle: {result['angle']} degrees",
                f"3. Time of flight: {result['time_flight']:.2f} s",
                f"4. Maximum height: {result['max_height']:.2f} m",
                f"5. Range: {result['range']:.2f} m"
            ]
        elif problem.problem_type == ProblemType.FREE_FALL:
            steps = [
                f"1. Initial height: {result['height']} m",
                f"2. Time of fall: {result['time_fall']:.2f} s",
                f"3. Final velocity: {result['final_velocity']:.2f} m/s"
            ]
        elif problem.problem_type == ProblemType.PENDULUM:
            steps = [
                f"1. Pendulum length: {result['length']} m",
                f"2. Period: {result['period']:.2f} s",
                f"3. Frequency: {result['frequency']:.2f} Hz"
            ]
        elif problem.problem_type == ProblemType.COLLISION:
            steps = [
                f"1. Ball A mass: {result['mass_a']} kg, initial velocity: {result['velocity_a']} m/s",
                f"2. Ball B mass: {result['mass_b']} kg, initial velocity: {result['velocity_b']} m/s",
                f"3. Final velocity of Ball A: {result['velocity_a_final']:.2f} m/s",
                f"4. Final velocity of Ball B: {result['velocity_b_final']:.2f} m/s"
            ]
        
        return steps

    def _get_llm_solution(self, problem: PhysicsProblem) -> dict:
        """Use LLM to solve the physics problem"""
        try:
            # Convert problem to text description
            problem_text = f"""
            Problem Type: {problem.problem_type.value}
            Initial Conditions: {problem.initial_conditions}
            Objects: {[obj.__dict__ for obj in problem.objects]}
            Question: {problem.question}
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """You are a physics problem solver. Your task is to:
1. Solve the given physics problem
2. Return a JSON object with:
   - answer: The numerical answer
   - unit: The unit of measurement
   - steps: List of steps to solve the problem
   - method: The method used (e.g., "analytical", "conservation_of_energy", etc.)

For each problem type, use these methods:
- PROJECTILE: Use kinematic equations
- FREE_FALL: Use conservation of energy
- PENDULUM: Use small angle approximation
- COLLISION: Use conservation of momentum and energy

Example output:
{
    "answer": 40.8,
    "unit": "m",
    "steps": [
        "Step 1: Use conservation of energy",
        "Step 2: Calculate final velocity",
        "Step 3: Convert to distance"
    ],
    "method": "conservation_of_energy"
}"""},
                    {"role": "user", "content": problem_text}
                ]
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Debug PhysicsSolver: Error in LLM solution - {str(e)}")
            return None