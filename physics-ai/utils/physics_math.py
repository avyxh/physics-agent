import numpy as np
import sympy as sp
from typing import Dict, List, Tuple, Any
from config.settings import Config
import math

class PhysicsMath:
    @staticmethod
    def projectile_motion(v0: float, angle: float, height: float = 0) -> Dict[str, float]:
        """
        Calculate projectile motion parameters
        
        Args:
            v0: Initial velocity (m/s)
            angle: Launch angle (degrees)
            height: Initial height (m)
        
        Returns:
            Dictionary containing:
            - range: Horizontal distance traveled (m)
            - time_flight: Time of flight (s)
            - max_height: Maximum height reached (m)
            - final_velocity: Final velocity magnitude (m/s)
            - final_velocity_x: Final x-velocity (m/s)
            - final_velocity_y: Final y-velocity (m/s)
        """
        print(f"Debug PhysicsMath: v0={v0}, angle={angle}, height={height}")
        
        # Convert angle to radians
        angle_rad = math.radians(angle)
        
        # Calculate initial velocity components
        v0x = v0 * math.cos(angle_rad)
        v0y = v0 * math.sin(angle_rad)
        print(f"Debug PhysicsMath: v0x={v0x:.2f}, v0y={v0y:.2f}")
        
        # Calculate time of flight using quadratic equation
        # y = y0 + v0y*t - 0.5*g*t^2
        # When y = 0 (ground level), solve for t
        # 0 = height + v0y*t - 0.5*g*t^2
        # 0.5*g*t^2 - v0y*t - height = 0
        
        a = 0.5 * Config.GRAVITY
        b = -v0y
        c = -height
        
        discriminant = b**2 - 4*a*c
        print(f"Debug PhysicsMath: discriminant={discriminant}")
        
        if discriminant < 0:
            raise ValueError("Projectile will not reach the ground")
        
        # Use the positive root for time of flight
        time_flight = (-b + math.sqrt(discriminant)) / (2*a)
        print(f"Debug PhysicsMath: time_flight={time_flight:.2f}")
        
        # Calculate range
        range_x = v0x * time_flight
        print(f"Debug PhysicsMath: range_x={range_x:.2f}")
        
        # Calculate maximum height
        # At max height, vy = 0
        # vy = v0y - g*t
        # 0 = v0y - g*t
        # t = v0y/g
        time_to_max_height = v0y / Config.GRAVITY
        max_height = height + v0y * time_to_max_height - 0.5 * Config.GRAVITY * time_to_max_height**2
        
        # Calculate final velocity components
        final_velocity_x = v0x  # No air resistance, so x-velocity remains constant
        final_velocity_y = v0y - Config.GRAVITY * time_flight
        
        # Calculate final velocity magnitude
        final_velocity = math.sqrt(final_velocity_x**2 + final_velocity_y**2)
        
        result = {
            'range': range_x,
            'time_flight': time_flight,
            'max_height': max_height,
            'final_velocity': final_velocity,
            'final_velocity_x': final_velocity_x,
            'final_velocity_y': final_velocity_y
        }
        print(f"Debug PhysicsMath: final result={result}")
        
        return result
    
    @staticmethod
    def free_fall(height: float, initial_velocity: float = 0) -> Dict[str, float]:
        """Calculate free fall motion"""
        g = Config.GRAVITY
        
        # Time to fall: h = v0*t + 0.5*g*t^2
        # Rearranged: 0.5*g*t^2 + v0*t - h = 0
        a, b, c = 0.5 * g, initial_velocity, -height
        discriminant = b**2 - 4*a*c
        
        if discriminant >= 0:
            time = (-b + np.sqrt(discriminant)) / (2*a)
        else:
            time = 0
        
        # Final velocity: v = v0 + g*t
        final_velocity = initial_velocity + g * time
        
        return {
            'time': time,
            'final_velocity': final_velocity
        }
    
    @staticmethod
    def collision_1d(m1: float, v1: float, m2: float, v2: float, 
                     coefficient_restitution: float = 1.0) -> Tuple[float, float]:
        """Calculate 1D collision final velocities"""
        
        # Conservation of momentum: m1*v1 + m2*v2 = m1*v1f + m2*v2f
        # Coefficient of restitution: e = (v2f - v1f) / (v1 - v2)
        
        total_momentum = m1 * v1 + m2 * v2
        relative_velocity = v1 - v2
        
        # Solve system of equations
        v1f = (total_momentum - m2 * coefficient_restitution * relative_velocity) / (m1 + m2)
        v2f = v1f + coefficient_restitution * relative_velocity
        
        return v1f, v2f
    
    @staticmethod
    def pendulum_motion(length: float, angle_max: float) -> Dict[str, float]:
        """Calculate pendulum motion parameters"""
        g = Config.GRAVITY
        
        # Small angle approximation period
        period_small = 2 * np.pi * np.sqrt(length / g)
        
        # More accurate period for larger angles
        angle_rad = np.radians(angle_max)
        k = np.sin(angle_rad / 2)
        # Elliptic integral approximation
        period_accurate = period_small * (1 + 0.25 * k**2 + 0.0625 * k**4)
        
        # Maximum velocity (at bottom)
        v_max = np.sqrt(2 * g * length * (1 - np.cos(angle_rad)))
        
        return {
            'period_small_angle': period_small,
            'period_accurate': period_accurate,
            'max_velocity': v_max,
            'frequency': 1 / period_accurate
        }