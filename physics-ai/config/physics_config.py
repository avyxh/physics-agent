"""Configuration for physics simulation parameters"""

class PhysicsConfig:
    # General physics constants
    GRAVITY = 9.81  # m/s^2
    TIME_STEP = 1/240  # seconds
    MAX_SIMULATION_STEPS = 1000

    # Collision parameters
    COLLISION = {
        'ball_radius': 0.1,  # meters
        'collision_threshold': 0.2,  # meters
        'separation_threshold': 0.2,  # meters
        'initial_separation': 1.0,  # meters
        'restitution': 1.0,  # elastic collision
        'friction': 0.0,  # no friction
    }

    # Pendulum parameters
    PENDULUM = {
        'bob_radius': 0.1,  # meters
        'string_length': 1.0,  # meters
        'initial_angle': 30.0,  # degrees
        'damping': 0.0,  # no damping
    }

    # Projectile parameters
    PROJECTILE = {
        'object_radius': 0.1,  # meters
        'air_resistance': 0.0,  # no air resistance
        'default_angle': 45.0,  # degrees
    }

    # Free fall parameters
    FREE_FALL = {
        'object_radius': 0.1,  # meters
        'air_resistance': 0.0,  # no air resistance
    }

    # Simulation parameters
    SIMULATION = {
        'gravity': [0, 0, -GRAVITY],  # m/s^2
        'time_step': TIME_STEP,  # seconds
        'max_steps': MAX_SIMULATION_STEPS,
        'debug_mode': False,  # enable/disable debug output
    } 