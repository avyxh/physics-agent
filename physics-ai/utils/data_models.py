# utils/data_models.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class ProblemType(Enum):
    """Types of physics problems that can be solved"""
    GENERAL = "general"
    KINEMATICS = "kinematics"
    PROJECTILE = "projectile"
    FREE_FALL = "free_fall"
    PENDULUM = "pendulum"
    COLLISION = "collision"
    SPRING = "spring"
    CIRCULAR = "circular"
    OTHER = "other"

class InputType(Enum):
    """Types of input that can be processed"""
    TEXT = "text"
    IMAGE = "image"
    INTERACTIVE = "interactive"

@dataclass
class PhysicsObject:
    """Represents a physical object in the problem"""
    name: str
    mass: float = 1.0
    position: List[float] = None
    velocity: List[float] = None
    acceleration: List[float] = None
    forces: List[Dict[str, Any]] = None
    length: Optional[float] = None
    height: Optional[float] = None
    
    def __post_init__(self):
        if self.position is None:
            self.position = [0.0, 0.0, 0.0]
        if self.velocity is None:
            self.velocity = [0.0, 0.0, 0.0]
        if self.acceleration is None:
            self.acceleration = [0.0, 0.0, 0.0]
        if self.forces is None:
            self.forces = []

@dataclass
class PhysicsProblem:
    """Represents a physics problem to be solved"""
    problem_text: str
    problem_type: ProblemType
    objects: List[PhysicsObject]
    initial_conditions: Dict[str, Any]
    constraints: List[str]
    question: str
    input_type: InputType = InputType.TEXT
    expected_answer_type: str = "unknown"

@dataclass
class Solution:
    """Represents a solution to a physics problem"""
    answer: float
    unit: str
    method: str
    steps: List[str]
    confidence: float = 1.0
    visualization_data: Optional[Dict[str, Any]] = None
    alternative_methods: Optional[List[str]] = None
    analytical_result: Optional[Dict[str, Any]] = None

@dataclass
class VerificationResult:
    """Result of solution verification"""
    is_valid: bool
    confidence: float
    error: Optional[str] = None
    analytical_result: Any = None
    simulation_result: Any = None
    agreement_score: float = 0.0