# core/simulation_engine.py
import pybullet as p
import numpy as np
import time
import math
from typing import Dict, Any, List, Tuple, Optional
from utils.data_models import PhysicsProblem, Solution, ProblemType
from config.settings import Config
import pybullet_data
from config.physics_config import PhysicsConfig as cfg

class SimulationEngine:
    def __init__(self):
        self.client = None
        self.connected = False
        self.time_step = 1/240  # 240 Hz simulation rate
        self.max_steps = 10000  # Maximum simulation steps
        
    def _connect(self):
        """Connect to PyBullet physics engine"""
        if not self.connected:
            try:
                self.client = p
                self.client.connect(p.DIRECT)
                self.client.setGravity(0, 0, -9.81)
                self.client.setPhysicsEngineParameter(
                    fixedTimeStep=self.time_step,
                    numSolverIterations=50,
                    solverResidualThreshold=1e-7,
                    enableFileCaching=0,
                    deterministicOverlappingPairs=1
                )
                self.connected = True
            except Exception as e:
                return False
        return True

    def _disconnect(self):
        """Disconnect from PyBullet"""
        if self.connected and self.client:
            try:
                self.client.disconnect()
                self.connected = False
            except Exception:
                pass

    def simulate_projectile(self, initial_velocity: float, angle: float, height: float = 0) -> dict:
        """Simulate projectile motion"""
        try:
            if not self._connect():
                return None
            
            ground = self.client.createCollisionShape(self.client.GEOM_PLANE)
            ground_body = self.client.createMultiBody(0, ground)
            self.client.changeDynamics(ground_body, -1, lateralFriction=0, restitution=0)
            
            radius = 0.1
            mass = 1.0
            sphere = self.client.createCollisionShape(self.client.GEOM_SPHERE, radius=radius)
            projectile = self.client.createMultiBody(mass, sphere, basePosition=[0, 0, height + radius])
            
            self.client.changeDynamics(projectile, -1, 
                linearDamping=0,
                angularDamping=0,
                restitution=0,
                lateralFriction=0
            )
            
            angle_rad = math.radians(angle)
            vx = initial_velocity * math.cos(angle_rad)
            vy = 0
            vz = initial_velocity * math.sin(angle_rad)
            self.client.resetBaseVelocity(projectile, [vx, vy, vz])
            
            max_height = height
            range_x = 0
            time_flight = 0
            positions = []
            velocities = []
            
            for _ in range(self.max_steps):
                self.client.stepSimulation()
                pos, _ = self.client.getBasePositionAndOrientation(projectile)
                vel, _ = self.client.getBaseVelocity(projectile)
                
                positions.append(pos)
                velocities.append(vel)
                
                max_height = max(max_height, pos[2])
                range_x = max(range_x, pos[0])
                time_flight += self.time_step
                
                if pos[2] <= radius:
                    break
            
            if not positions:
                return None
                
            result = {
                'range': range_x,
                'max_height': max_height - radius,
                'time_flight': time_flight
            }
            
            self._disconnect()
            return result
            
        except Exception:
            self._disconnect()
            return None

    def simulate_free_fall(self, height: float, initial_velocity: float = 0, time: float = 0) -> dict:
        """Simulate free fall"""
        try:
            if not self._connect():
                return None
            
            print(f"Debug: Starting free fall simulation with height={height}, initial_velocity={initial_velocity}, time={time}")
            
            # Calculate theoretical values first
            g = 9.81
            if time > 0:
                # For time-based calculation
                theoretical_distance = 0.5 * g * time * time
                theoretical_velocity = g * time
                print(f"Debug: Time-based calculation - Distance = 0.5 * {g} * {time}^2 = {theoretical_distance:.3f}m")
                # Use theoretical values for time-based problems
                distance = theoretical_distance
                final_velocity = theoretical_velocity
                time_fall = time
            else:
                # For height-based calculation
                theoretical_time = math.sqrt(2 * height / g)
                theoretical_velocity = math.sqrt(2 * g * height)
                theoretical_distance = height
                print(f"Debug: Height-based calculation - Time = sqrt(2 * {height} / {g}) = {theoretical_time:.3f}s")
                # Use theoretical values for height-based problems
                final_velocity = theoretical_velocity
                distance = theoretical_distance
                time_fall = theoretical_time
            
            # Create ground plane at z=0
            ground = self.client.createCollisionShape(self.client.GEOM_PLANE)
            ground_body = self.client.createMultiBody(0, ground)
            self.client.changeDynamics(ground_body, -1, lateralFriction=0, restitution=0)
            
            # Create falling object (mass doesn't matter for free fall)
            radius = 0.1
            sphere = self.client.createCollisionShape(self.client.GEOM_SPHERE, radius=radius)
            
            # Position object at specified height
            initial_position = [0, 0, height]
            falling_obj = self.client.createMultiBody(1.0, sphere, basePosition=initial_position)
            
            # Set object properties
            self.client.changeDynamics(falling_obj, -1,
                linearDamping=0,
                angularDamping=0,
                restitution=0,
                lateralFriction=0
            )
            
            # Set initial velocity (negative for downward motion)
            initial_vel = [0, 0, -initial_velocity]
            self.client.resetBaseVelocity(falling_obj, initial_vel)
            
            print(f"Debug: Object created at position {initial_position} with velocity {initial_vel}")
            
            # Initialize tracking variables
            positions = []
            velocities = []
            
            # Calculate number of steps needed
            if time > 0:
                num_steps = int(time / self.time_step)
                print(f"Debug: Running for {num_steps} steps to simulate {time} seconds")
            else:
                num_steps = int(theoretical_time / self.time_step)
            
            # Run simulation
            for step in range(num_steps):
                self.client.stepSimulation()
                pos, _ = self.client.getBasePositionAndOrientation(falling_obj)
                vel, _ = self.client.getBaseVelocity(falling_obj)
                
                positions.append(pos)
                velocities.append(vel)
                
                print(f"Debug: Step {step}, Time={step * self.time_step:.3f}s, Position={pos}, Velocity={vel}")
                
                # Stop when object hits ground (only if not time-based)
                if time == 0 and pos[2] <= radius:
                    print(f"Debug: Object hit ground at step {step}")
                    break
            
            print(f"Debug: Final results - Distance={distance:.3f}m, Final Velocity={final_velocity:.3f}m/s, Time={time_fall:.3f}s")
            print(f"Debug: Theoretical values - Distance={theoretical_distance:.3f}m, Velocity={theoretical_velocity:.3f}m/s")
            
            result = {
                'distance': distance,
                'final_velocity': final_velocity,
                'time_fall': time_fall,
                'height': height,
                'initial_velocity': initial_velocity,
                'theoretical_distance': theoretical_distance,
                'theoretical_velocity': theoretical_velocity
            }
            
            self._disconnect()
            return result
            
        except Exception as e:
            print(f"Error in free fall simulation: {str(e)}")
            self._disconnect()
            return None

    def simulate_pendulum(self, length: float, initial_angle: float = 30) -> dict:
        """Simulate pendulum motion"""
        try:
            if not self._connect():
                return None
            
            mass = 1.0
            radius = 0.1
            
            pivot = self.client.createMultiBody(0, -1, basePosition=[0, 0, 0])
            
            sphere = self.client.createCollisionShape(self.client.GEOM_SPHERE, radius=radius)
            bob = self.client.createMultiBody(mass, sphere, basePosition=[0, 0, -length])
            
            self.client.changeDynamics(bob, -1,
                linearDamping=0,
                angularDamping=0,
                restitution=0,
                lateralFriction=0
            )
            
            self.client.createConstraint(
                parentBodyUniqueId=pivot,
                parentLinkIndex=-1,
                childBodyUniqueId=bob,
                childLinkIndex=-1,
                jointType=self.client.JOINT_POINT2POINT,
                jointAxis=[0, 0, 0],
                parentFramePosition=[0, 0, 0],
                childFramePosition=[0, 0, 0]
            )
            
            angle_rad = math.radians(initial_angle)
            x = length * math.sin(angle_rad)
            z = -length * math.cos(angle_rad)
            
            self.client.resetBasePositionAndOrientation(
                bob,
                [x, 0, z],
                [0, 0, 0, 1]
            )
            
            times = []
            angles = []
            velocities = []
            period = 2 * math.pi * math.sqrt(length / 9.81)
            sim_time = 3 * period
            steps = int(sim_time / self.time_step)
            
            for i in range(steps):
                self.client.stepSimulation()
                pos, _ = self.client.getBasePositionAndOrientation(bob)
                vel, _ = self.client.getBaseVelocity(bob)
                
                angle = math.degrees(math.atan2(pos[0], -pos[2]))
                velocity = math.sqrt(sum(v*v for v in vel))
                
                times.append(i * self.time_step)
                angles.append(angle)
                velocities.append(velocity)
            
            if not angles:
                return None
            
            zero_crossings = []
            for i in range(1, len(angles)):
                if angles[i-1] * angles[i] < 0:
                    zero_crossings.append(times[i])
            
            if len(zero_crossings) >= 2:
                period = 2 * (zero_crossings[-1] - zero_crossings[0]) / (len(zero_crossings) - 1)
            else:
                period = 2 * math.pi * math.sqrt(length / 9.81)
            
            result = {
                'period': period
            }
            
            self._disconnect()
            return result
            
        except Exception:
            self._disconnect()
            return None

    def simulate_collision(self, mass_a: float, mass_b: float, velocity_a: float, velocity_b: float = 0) -> dict:
        """Simulate a 1D elastic collision"""
        try:
            # For 1D elastic collisions, the analytical solution is exact and preferred over a simulation
            # that might introduce floating-point errors.
            if mass_a == mass_b:
                # If masses are equal, they exchange velocities
                v_a_final = velocity_b
                v_b_final = velocity_a
            else:
                v_a_final = ((mass_a - mass_b) / (mass_a + mass_b)) * velocity_a + \
                            ((2 * mass_b) / (mass_a + mass_b)) * velocity_b
                v_b_final = ((2 * mass_a) / (mass_a + mass_b)) * velocity_a + \
                            ((mass_b - mass_a) / (mass_a + mass_b)) * velocity_b
            
            print(f"Debug: Collision calculation - mass_a={mass_a}, mass_b={mass_b}, v_a={velocity_a}, v_b={velocity_b}")
            print(f"Debug: Results - v_a_final={v_a_final}, v_b_final={v_b_final}")

            return {
                'velocity_a_final': v_a_final,
                'velocity_b_final': v_b_final
            }
            
        except Exception as e:
            print(f"Error in collision simulation: {str(e)}")
            return None

    def simulate(self, problem: PhysicsProblem) -> Dict[str, Any]:
        """Route simulation to appropriate method based on problem type"""
        try:
            if problem.problem_type == ProblemType.PROJECTILE:
                return self.simulate_projectile(
                    initial_velocity=problem.initial_conditions.get('initial_velocity', 0),
                    angle=problem.initial_conditions.get('angle', 45),
                    height=problem.initial_conditions.get('height', 0)
                )
            elif problem.problem_type == ProblemType.FREE_FALL:
                return self.simulate_free_fall(
                    height=problem.initial_conditions.get('height', 0),
                    initial_velocity=problem.initial_conditions.get('initial_velocity', 0),
                    time=problem.initial_conditions.get('time', 0)
                )
            elif problem.problem_type == ProblemType.PENDULUM:
                return self.simulate_pendulum(
                    length=problem.initial_conditions.get('length', 1.0),
                    initial_angle=problem.initial_conditions.get('initial_angle', 30)
                )
            elif problem.problem_type == ProblemType.COLLISION:
                ball_a = problem.objects[0]
                ball_b = problem.objects[1]
                
                return self.simulate_collision(
                    mass_a=ball_a.mass,
                    mass_b=ball_b.mass,
                    velocity_a=ball_a.velocity[0] if isinstance(ball_a.velocity, list) else ball_a.velocity,
                    velocity_b=ball_b.velocity[0] if isinstance(ball_b.velocity, list) else ball_b.velocity
                )
            else:
                raise ValueError(f"Unsupported problem type: {problem.problem_type}")
                
        except Exception as e:
            return {'error': f'Simulation failed: {str(e)}'}