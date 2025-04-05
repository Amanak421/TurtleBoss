"""
Constants module used across multiple files.
"""


from geometry import Point
import numpy as np
from rigidobject import RigidType

# robot.py
LINEAR_CORRECTION = 0.98  # 1  # 0.98  # 0.96
ANGULAR_CORRECTION = 1  # 1.04  # 1.18
POSITION_NAMES = ['LEFT', 'CENTER', 'RIGHT']
STATE_NAMES = ['RELEASED', 'PRESSED']
BASE_POSITION = Point(0, 0, np.pi/2)
LINEAR_EPSILON = 0.01
ANGULAR_EPSILON = 0.03
MIN_LINEAR_VELOCITY = 0.1
MAX_LINEAR_VELOCITY = 0.3
MIN_ANGULAR_VELOCITY = 0.35
MAX_ANGULAR_VELOCITY = 1
LINEAR_KP = 1.5
LINEAR_KD = 0.5
ANGULAR_KP = 1  # 0.8
ANGULAR_KD = 0.5  # 0.3

# mapping.py
MAX_OBJECTS = {RigidType.POLE: 2, RigidType.BALL: 1}
MIN_MATCHES = 2
