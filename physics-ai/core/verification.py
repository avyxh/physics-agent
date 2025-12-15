# core/verification.py
import numpy as np
from typing import Dict, Any, List
from utils.data_models import PhysicsProblem, Solution, VerificationResult
from core.simulation_engine import SimulationEngine
from config.settings import Config
from utils.data_models import ProblemType

class VerificationEngine:
    def __init__(self, simulation_engine: SimulationEngine = None):
        self.simulation_engine = simulation_engine if simulation_engine else SimulationEngine()
        self.agreement_threshold = 0.1  # 10% difference threshold
        
    def _calculate_agreement_score(self, analytical: float, simulated: float) -> float:
        """Calculate how well the analytical and simulated results agree"""
        if analytical == 0 and simulated == 0:
            return 1.0
        if analytical == 0 or simulated == 0:
            return 0.0
            
        # Calculate relative difference
        relative_diff = abs(analytical - simulated) / max(abs(analytical), abs(simulated))
        # Convert to agreement score (1.0 = perfect agreement, 0.0 = completely different)
        return max(0.0, 1.0 - relative_diff)
        
    def verify_solution(self, problem: PhysicsProblem, solution: Solution) -> VerificationResult:
        """Verify a solution using simulation"""
        try:
            # Get simulation result
            sim_result = self.simulation_engine.simulate(problem)
            
            if not sim_result:
                return VerificationResult(
                    is_valid=False,
                    confidence=0.0,
                    error="Simulation failed to run",
                    simulation_result="Simulation failed"
                )
            
            # Compare results based on problem type
            if problem.problem_type == ProblemType.PROJECTILE:
                analytical = solution.answer
                simulated = sim_result.get('range', 0)
                unit = 'm'
                
            elif problem.problem_type == ProblemType.FREE_FALL:
                if problem.initial_conditions.get('quantity_asked') == 'final_velocity':
                    analytical = solution.answer
                    simulated = sim_result.get('final_velocity', 0)
                    unit = 'm/s'
                else:  # distance
                    analytical = solution.answer
                    simulated = sim_result.get('distance', 0)
                    unit = 'm'
                    
            elif problem.problem_type == ProblemType.PENDULUM:
                analytical = solution.answer
                simulated = sim_result.get('period', 0)
                unit = 's'
                
            elif problem.problem_type == ProblemType.COLLISION:
                # For collisions, we compare both final velocities
                analytical = solution.answer  # This is a list [v_a_final, v_b_final]
                simulated = [sim_result.get('velocity_a_final', 0), sim_result.get('velocity_b_final', 0)]
                unit = 'm/s'
                
            else:
                return VerificationResult(
                    is_valid=False,
                    confidence=0.0,
                    error="Problem type not supported for verification",
                    simulation_result="Unsupported problem type"
                )
            
            # Calculate agreement score
            if isinstance(analytical, list) and isinstance(simulated, list):
                # For collision problems, compare both velocities
                agreement_score = self._calculate_agreement_score(analytical[0], simulated[0]) * 0.5 + \
                                self._calculate_agreement_score(analytical[1], simulated[1]) * 0.5
            else:
                agreement_score = self._calculate_agreement_score(analytical, simulated)
            
            # Format simulation result for display
            if problem.problem_type == ProblemType.COLLISION:
                sim_display = f"Final velocities: Ball A = {simulated[0]:.2f} m/s, Ball B = {simulated[1]:.2f} m/s"
            else:
                sim_display = f"{simulated:.2f} {unit}"
            
            # Calculate confidence based on agreement score
            confidence = agreement_score
            
            # Check if solution is valid (agreement > threshold)
            is_valid = agreement_score > 0.8
            
            return VerificationResult(
                is_valid=is_valid,
                confidence=confidence,
                error=None,
                analytical_result=solution.answer,
                simulation_result=sim_display,
                agreement_score=agreement_score
            )
            
        except Exception as e:
            print(f"Error in verification: {str(e)}")
            return VerificationResult(
                is_valid=False,
                confidence=0.0,
                error=str(e),
                simulation_result=f"Error: {str(e)}"
            )
    
    def _verify_projectile_motion(self, problem: PhysicsProblem, solution: Solution) -> VerificationResult:
        """Verify projectile motion solution using simulation"""
        
        # Extract parameters
        initial_velocity = problem.initial_conditions.get('velocity', 20)
        angle = problem.initial_conditions.get('angle', 45)
        height = problem.initial_conditions.get('height', 0)
        
        print(f"Debug Verification: v0={initial_velocity}, angle={angle}, height={height}")
        
        # Run simulation
        sim_result = self.simulation_engine.verify_projectile_motion(
            initial_velocity=initial_velocity,
            angle=angle,
            height=height
        )
        print(f"Debug Verification: sim_result={sim_result}")
        
        # Check for simulation errors
        if 'error' in sim_result:
            print(f"Debug Verification: Simulation error: {sim_result['error']}")
            return VerificationResult(
                is_valid=False,
                confidence=0.0,
                error=f"Simulation failed: {sim_result['error']}",
                analytical_result=solution.answer,
                simulation_result=f"Simulation failed: {sim_result['error']}"
            )
        
        # Extract analytical value
        analytical_value = float(solution.answer.split()[0])  # Extract number from "X meters"
        print(f"Debug Verification: analytical_value={analytical_value}")
        
        # For projectile motion, we always compare range
        sim_value = sim_result['range']
        comparison_type = "range"
        
        print(f"Debug Verification: sim_value={sim_value}, comparison_type={comparison_type}")
        
        # Calculate agreement score
        if analytical_value != 0:
            agreement_score = 1.0 - min(abs(sim_value - analytical_value) / analytical_value, 1.0)
        else:
            agreement_score = 1.0 if sim_value == 0 else 0.0
        
        print(f"Debug Verification: agreement_score={agreement_score}")
        
        # Calculate confidence based on agreement score
        confidence = agreement_score
        print(f"Debug Verification: confidence={confidence}")
        
        # Check if solution is valid (agreement > threshold)
        is_valid = agreement_score > 0.8
        
        # Format simulation result with units
        sim_result_str = f"{sim_value:.2f} meters"
        
        return VerificationResult(
            is_valid=is_valid,
            confidence=confidence,
            error=None,
            analytical_result=solution.answer,
            simulation_result=sim_result_str,
            agreement_score=agreement_score
        )
    
    def _verify_free_fall(self, problem, analytical_solution: Solution) -> VerificationResult:
        """Verify free fall solution"""
        
        height = problem.initial_conditions.get('height', 10)
        initial_velocity = problem.initial_conditions.get('initial_velocity', 0)
        
        sim_result = self.simulation_engine.verify_free_fall(height, initial_velocity)
        
        if 'error' in sim_result:
            return VerificationResult(
                is_valid=False,
                confidence=0.3,
                error=sim_result['error'],
                analytical_result=analytical_solution.answer,
                simulation_result=sim_result['error']
            )
        
        analytical_value = self._extract_numerical_value(analytical_solution.answer)
        
        if "distance" in problem.question.lower() or "how far" in problem.question.lower():
            sim_value = sim_result['distance']
        elif "velocity" in problem.question.lower():
            sim_value = sim_result['final_velocity']
        elif "time" in problem.question.lower():
            sim_value = sim_result['time_fall']
        else:
            sim_value = sim_result['final_velocity']  # default
        
        agreement_score = self._calculate_agreement(analytical_value, sim_value)
        confidence = self._calculate_confidence(agreement_score)
        is_valid = agreement_score > 0.8
        
        return VerificationResult(
            is_valid=is_valid,
            confidence=confidence,
            error=None,
            analytical_result=analytical_solution.answer,
            simulation_result=f"{sim_value:.3f} (simulation)",
            agreement_score=agreement_score
        )
    
    def _verify_pendulum(self, problem: PhysicsProblem, solution: Solution) -> VerificationResult:
        """Verify pendulum solution"""
        try:
            # Get parameters
            length = problem.initial_conditions.get('length', 1.0)
            initial_angle = problem.initial_conditions.get('initial_angle', 30.0)
            
            # Run simulation
            sim_result = self.simulation_engine._simulate_pendulum(length, initial_angle)
            
            if 'error' in sim_result:
                return VerificationResult(
                    is_valid=False,
                    confidence=0.0,
                    error=f"Simulation error: {sim_result['error']}",
                    analytical_result=solution.answer,
                    simulation_result=f"Error: {sim_result['error']}"
                )
            
            # Compare with analytical solution
            analytical_value = float(solution.answer)
            sim_value = float(sim_result.get('period_accurate', 0))
            
            # Calculate agreement score
            agreement_score = self._calculate_agreement(analytical_value, sim_value)
            confidence = 0.95 if agreement_score > 0.9 else 0.7
            is_valid = agreement_score > 0.8
            
            return VerificationResult(
                is_valid=is_valid,
                confidence=confidence,
                error=None,
                analytical_result=solution.answer,
                simulation_result=f"Period: {sim_value:.3f}s",
                agreement_score=agreement_score
            )
            
        except Exception as e:
            return VerificationResult(
                is_valid=False,
                confidence=0.0,
                error=f"Verification error: {str(e)}",
                analytical_result=solution.answer,
                simulation_result=f"Error: {str(e)}"
            )
    
    def _verify_general(self, problem, analytical_solution: Solution) -> VerificationResult:
        """General verification for unrecognized problems"""
        
        return VerificationResult(
            is_valid=True,
            confidence=0.7,  # Moderate confidence without verification
            error=None,
            analytical_result=analytical_solution.answer,
            simulation_result="No simulation verification available",
            agreement_score=0.7
        )
    
    def _extract_numerical_value(self, answer_string: str) -> float:
        """Extract numerical value from answer string"""
        import re
        
        # Look for numbers in the string
        numbers = re.findall(r'-?\d+\.?\d*', str(answer_string))
        if numbers:
            return float(numbers[0])
        return None
    
    def _calculate_agreement(self, analytical: float, simulation: float) -> float:
        """Calculate agreement score between analytical and simulation results"""
        
        if analytical == 0 and simulation == 0:
            return 1.0
        
        if analytical == 0 or simulation == 0:
            return 0.0
        
        # Calculate relative error
        relative_error = abs(analytical - simulation) / max(abs(analytical), abs(simulation))
        
        # Convert to agreement score (1.0 = perfect agreement)
        agreement = max(0.0, 1.0 - relative_error)
        
        return agreement
    
    def _calculate_confidence(self, agreement_score: float) -> float:
        """Calculate overall confidence based on agreement"""
        
        if agreement_score >= Config.HIGH_CONFIDENCE_THRESHOLD:
            return min(0.99, agreement_score + 0.05)  # Boost high agreement
        elif agreement_score >= Config.MEDIUM_CONFIDENCE_THRESHOLD:
            return agreement_score
        else:
            return max(0.1, agreement_score - 0.1)  # Penalize low agreement
    
    def _verify_collision(self, problem: PhysicsProblem, solution: Solution) -> VerificationResult:
        """Verify collision results using simulation"""
        try:
            # Extract parameters from problem
            mass_a = problem.objects[0].mass
            velocity_a = problem.objects[0].velocity
            mass_b = problem.objects[1].mass
            velocity_b = problem.objects[1].velocity if problem.objects[1].velocity is not None else 0

            # Run simulation
            simulation_result = self.simulation_engine.verify_collision(
                mass_a=mass_a,
                mass_b=mass_b,
                velocity_a=velocity_a,
                velocity_b=velocity_b
            )

            if not simulation_result:
                return VerificationResult(
                    is_valid=False,
                    confidence=0.0,
                    error="Simulation failed to run",
                    analytical_result=solution.answer,
                    simulation_result="Simulation failed"
                )

            # Extract final velocities from simulation
            sim_velocity_a = simulation_result.get('velocity_a_final', 0)
            sim_velocity_b = simulation_result.get('velocity_b_final', 0)

            # Extract final velocities from analytical solution
            # Parse the answer string to get velocities
            answer_parts = solution.answer.split(',')
            analytical_velocity_a = float(answer_parts[0].split(':')[1].strip().split()[0])
            analytical_velocity_b = float(answer_parts[1].split(':')[1].strip().split()[0])

            # Calculate agreement scores for each ball
            agreement_a = 1.0 - min(abs(sim_velocity_a - analytical_velocity_a) / max(abs(analytical_velocity_a), 0.1), 1.0)
            agreement_b = 1.0 - min(abs(sim_velocity_b - analytical_velocity_b) / max(abs(analytical_velocity_b), 0.1), 1.0)

            # Overall agreement score is average of both balls
            agreement_score = (agreement_a + agreement_b) / 2

            # Calculate confidence based on agreement
            confidence = 0.95 if agreement_score > 0.9 else 0.7 if agreement_score > 0.7 else 0.3

            # Check if solution is valid
            is_valid = agreement_score > 0.7

            return VerificationResult(
                is_valid=is_valid,
                confidence=confidence,
                error=None,
                analytical_result=solution.answer,
                simulation_result=f"Ball A: {sim_velocity_a:.2f} m/s, Ball B: {sim_velocity_b:.2f} m/s",
                agreement_score=agreement_score
            )

        except Exception as e:
            print(f"Error verifying collision: {str(e)}")
            return VerificationResult(
                is_valid=False,
                confidence=0.0,
                error=f"Verification error: {str(e)}",
                analytical_result=solution.answer,
                simulation_result="Verification failed"
            )