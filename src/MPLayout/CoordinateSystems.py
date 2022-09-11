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
        return cylinder_to_cart(self).__call__()

@dataclass
class VectorSphere:
    r: float = 0
    phi: float = 0
    theta: float = 0

    def __call__(self) -> np.ndarray:
        return sphere_to_cart(self).__call__()

def cylinder_to_cart(v: VectorCylinder) -> VectorCart:
    return VectorCart(
        x=v.r*np.cos(v.phi),
        y=v.r*np.sin(v.phi),
        z=v.z
    )

def cart_to_cylinder(v: VectorCart) -> VectorCylinder:
    return VectorCylinder(
        r=np.sqrt(v.x**2+v.y**2),
        phi=np.arctan2(v.y, v.x),
        z=v.z
    )

def sphere_to_cart(v: VectorSphere) -> VectorCart:
    return VectorCart(
        x=v.r*np.sin(v.theta)*np.cos(v.phi),
        y=v.r*np.sin(v.theta)*np.sin(v.phi),
        z=v.r*np.cos(v.theta)
    )

def cart_vector(v: np.ndarray) -> VectorCart:
    return VectorCart(x=v[0], y=v[1], z=v[2])

def vector_norm(v: Vector) -> float:
    return np.sqrt(np.sum(v()**2))