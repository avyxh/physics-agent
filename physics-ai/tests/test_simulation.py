# tests/test_simulation.py
import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.simulation_engine import SimulationEngine
import numpy as np

class TestSimulationEngine(unittest.TestCase):
    
    def setUp(self):
        self.sim_engine = SimulationEngine()
    
    def test_projectile_motion_simulation(self):
        """Test projectile motion simulation"""
        result = self.sim_engine.verify_projectile_motion(
            initial_velocity=20,
            angle=45,
            height=0
        )
        
        self.assertNotIn('error', result)
        self.assertIn('range', result)
        self.assertIn('time_flight', result)
        
        # Check if results are reasonable
        self.assertGreater(result['range'], 30)  # Should be around 40m
        self.assertLess(result['range'], 50)
        self.assertGreater(result['time_flight'], 2)  # Should be around 2.9s
        self.assertLess(result['time_flight'], 4)
    
    def test_free_fall_simulation(self):
        """Test free fall simulation"""
        result = self.sim_engine.verify_free_fall(height=20, initial_velocity=0)
        
        self.assertNotIn('error', result)
        self.assertIn('final_velocity', result)
        self.assertIn('time', result)
        
        # Check physics: v = √(2gh) = √(2*9.81*20) ≈ 19.8 m/s
        expected_velocity = np.sqrt(2 * 9.81 * 20)
        self.assertAlmostEqual(result['final_velocity'], expected_velocity, delta=1.0)
    
    def test_simulation_engine_connection(self):
        """Test simulation engine can connect and disconnect"""
        # Should be able to connect
        self.sim_engine.connect()
        self.assertTrue(self.sim_engine.is_connected)
        
        # Should be able to disconnect
        self.sim_engine.disconnect()
        self.assertFalse(self.sim_engine.is_connected)
    
    def test_multiple_simulations(self):
        """Test running multiple simulations in sequence"""
        # Run first simulation
        result1 = self.sim_engine.verify_projectile_motion(20, 45, 0)
        
        # Run second simulation
        result2 = self.sim_engine.verify_projectile_motion(25, 30, 0)
        
        # Both should succeed
        self.assertNotIn('error', result1)
        self.assertNotIn('error', result2)
        
        # Results should be different
        self.assertNotEqual(result1['range'], result2['range'])

if __name__ == '__main__':
    unittest.main()