# tests/test_solver.py
import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.physics_solver import PhysicsSolver
from core.problem_parser import ProblemParser
from utils.data_models import PhysicsProblem, ProblemType, InputType

class TestPhysicsSolver(unittest.TestCase):
    
    def setUp(self):
        self.solver = PhysicsSolver()
        self.parser = ProblemParser()
    
    def test_free_fall_problem(self):
        """Test free fall calculation"""
        problem_text = "A ball is dropped from 20m height. What is its final velocity?"
        
        # Parse the problem
        problem = self.parser.parse_text_problem(problem_text)
        
        # Solve the problem
        solution = self.solver.solve_problem(problem)
        
        # Check the solution
        self.assertIsNotNone(solution)
        self.assertGreater(solution.confidence, 0.8)
        self.assertIn("19.8", solution.answer)  # Expected velocity ~19.8 m/s
    
    def test_projectile_motion(self):
        """Test projectile motion calculation"""
        problem_text = "A ball is thrown at 45 degrees with initial velocity 20 m/s. How far does it travel?"
        
        problem = self.parser.parse_text_problem(problem_text)
        solution = self.solver.solve_problem(problem)
        
        self.assertIsNotNone(solution)
        self.assertGreater(solution.confidence, 0.8)
        # Expected range = v²sin(2θ)/g = 400*sin(90)/9.81 ≈ 40.8m
        self.assertIn("40", solution.answer)
    
    def test_pendulum_motion(self):
        """Test pendulum period calculation"""
        problem_text = "A pendulum has length 1.0m. What is its period?"
        
        problem = self.parser.parse_text_problem(problem_text)
        solution = self.solver.solve_problem(problem)
        
        self.assertIsNotNone(solution)
        self.assertGreater(solution.confidence, 0.8)
        # Expected period = 2π√(L/g) = 2π√(1/9.81) ≈ 2.0s
        self.assertIn("2.0", solution.answer)
    
    def test_step_by_step_solution(self):
        """Test that solutions include step-by-step explanations"""
        problem_text = "A ball drops from 10m. Find final velocity."
        
        problem = self.parser.parse_text_problem(problem_text)
        solution = self.solver.solve_problem(problem)
        
        self.assertIsNotNone(solution.steps)
        self.assertGreater(len(solution.steps), 2)
        self.assertTrue(any("kinematic" in step.lower() for step in solution.steps))
    
    def test_unknown_problem_type(self):
        """Test handling of unknown problem types"""
        problem_text = "Calculate the flux capacitor resonance frequency."
        
        problem = self.parser.parse_text_problem(problem_text)
        solution = self.solver.solve_problem(problem)
        
        # Should not crash, should return low confidence
        self.assertIsNotNone(solution)
        self.assertLess(solution.confidence, 0.5)

if __name__ == '__main__':
    unittest.main()