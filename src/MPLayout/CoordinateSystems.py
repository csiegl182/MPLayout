from dataclasses import dataclass
from typing import Protocol
import numpy as np

class Vector(Protocol):
    def __call__(self) -> np.ndarray:
        pass

@dataclass
class VectorCart:
    x: float = 0
    y: float = 0
    z: float = 0

    def __call__(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

@dataclass
class VectorCylinder:
    r: float = 0
    phi: float = 0
    z: float = 0

    def __call__(self) -> np.ndarray:
        return Cylinder2Cart(self).__call__()

@dataclass
class VectorSphere:
    r: float = 0
    phi: float = 0
    theta: float = 0

    def __call__(self) -> np.ndarray:
        return Sphere2Cart(self).__call__()

def Cylinder2Cart(v: VectorCylinder) -> VectorCart:
    return VectorCart(
        x=v.r*np.cos(v.phi),
        y=v.r*np.sin(v.phi),
        z=v.z
    )

def Sphere2Cart(v: VectorSphere) -> VectorCart:
    return VectorCart(
        x=v.r*np.sin(v.theta)*np.cos(v.phi),
        y=v.r*np.sin(v.theta)*np.sin(v.phi),
        z=v.r*np.cos(v.theta)
    )

def vector_norm(v: Vector) -> float:
    return np.sqrt(np.sum(v()**2))