"""
Stress & Strain Calculator
Covers: Normal stress, Shear stress, Von Mises, Factor of Safety, Thermal stress
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class StressType(Enum):
    NORMAL = "normal"
    SHEAR = "shear"
    BENDING = "bending"
    TORSIONAL = "torsional"


@dataclass
class StressResult:
    stress_MPa: float
    strain: Optional[float]
    factor_of_safety: Optional[float]
    von_mises_MPa: Optional[float]
    failure_mode: Optional[str]
    safe: bool
    formula_used: str


def normal_stress(force_N: float, area_m2: float) -> float:
    """σ = F/A — axial normal stress in Pa"""
    if area_m2 <= 0:
        raise ValueError("Area must be positive")
    return force_N / area_m2


def shear_stress(shear_force_N: float, area_m2: float) -> float:
    """τ = V/A — average shear stress in Pa"""
    if area_m2 <= 0:
        raise ValueError("Area must be positive")
    return shear_force_N / area_m2


def bending_stress(
    moment_Nm: float,
    distance_from_neutral_m: float,
    moment_of_inertia_m4: float,
) -> float:
    """σ = My/I — flexural / bending stress in Pa"""
    if moment_of_inertia_m4 <= 0:
        raise ValueError("Moment of inertia must be positive")
    return (moment_Nm * distance_from_neutral_m) / moment_of_inertia_m4


def torsional_shear_stress(
    torque_Nm: float,
    radius_m: float,
    polar_moment_m4: float,
) -> float:
    """τ = Tr/J — torsional shear stress in Pa"""
    if polar_moment_m4 <= 0:
        raise ValueError("Polar moment must be positive")
    return (torque_Nm * radius_m) / polar_moment_m4


def von_mises_stress(
    sigma_x: float,
    sigma_y: float = 0.0,
    tau_xy: float = 0.0,
    sigma_z: float = 0.0,
) -> float:
    """
    Von Mises equivalent stress (Pa) for combined loading.
    σ_vm = sqrt(σx² - σxσy + σy² + 3τxy²)  (plane stress simplification)
    Full 3D: σ_vm = sqrt(0.5*[(σx-σy)² + (σy-σz)² + (σz-σx)² + 6τxy²])
    """
    return math.sqrt(
        0.5 * (
            (sigma_x - sigma_y) ** 2
            + (sigma_y - sigma_z) ** 2
            + (sigma_z - sigma_x) ** 2
            + 6 * tau_xy ** 2
        )
    )


def thermal_stress(
    elastic_modulus_GPa: float,
    thermal_expansion_coeff: float,  # 1/°C  e.g. 12e-6 for steel
    delta_temp_C: float,
) -> float:
    """σ_thermal = E * α * ΔT (Pa) — stress in fully constrained member"""
    E = elastic_modulus_GPa * 1e9
    return E * thermal_expansion_coeff * delta_temp_C


def calculate_stress(
    stress_type: StressType,
    yield_strength_MPa: float,
    elastic_modulus_GPa: float = 200.0,
    # Normal / bending stress inputs
    force_N: float = 0.0,
    area_m2: float = 1e-4,
    # Bending inputs
    moment_Nm: float = 0.0,
    distance_m: float = 0.0,
    moment_of_inertia_m4: float = 1e-8,
    # Shear / torsion inputs
    shear_force_N: float = 0.0,
    torque_Nm: float = 0.0,
    radius_m: float = 0.0,
    polar_moment_m4: float = 1e-8,
    # Combined loading (Von Mises)
    sigma_x_MPa: float = 0.0,
    sigma_y_MPa: float = 0.0,
    tau_xy_MPa: float = 0.0,
) -> StressResult:
    """
    Calculate stress and determine safety based on yield strength.
    """
    sigma_y = yield_strength_MPa * 1e6
    strain = None
    vm_MPa = None
    fos = None
    failure_mode = None

    E = elastic_modulus_GPa * 1e9

    if stress_type == StressType.NORMAL:
        sigma = normal_stress(force_N, area_m2)
        strain = sigma / E
        fos = sigma_y / abs(sigma) if sigma != 0 else float("inf")
        failure_mode = "Yielding (tensile)" if sigma > 0 else "Yielding (compressive)"
        formula = "σ = F/A"

    elif stress_type == StressType.BENDING:
        sigma = bending_stress(moment_Nm, distance_m, moment_of_inertia_m4)
        strain = sigma / E
        fos = sigma_y / abs(sigma) if sigma != 0 else float("inf")
        failure_mode = "Flexural yielding"
        formula = "σ = My/I"

    elif stress_type == StressType.SHEAR:
        tau = shear_stress(shear_force_N, area_m2)
        sigma = tau
        # Tresca criterion: yielding in shear at τ_yield = σ_y / 2
        tau_yield = sigma_y / 2
        fos = tau_yield / abs(tau) if tau != 0 else float("inf")
        failure_mode = "Shear yielding (Tresca)"
        formula = "τ = V/A"

    elif stress_type == StressType.TORSIONAL:
        tau = torsional_shear_stress(torque_Nm, radius_m, polar_moment_m4)
        sigma = tau
        tau_yield = sigma_y / 2
        fos = tau_yield / abs(tau) if tau != 0 else float("inf")
        failure_mode = "Torsional shear yielding"
        formula = "τ = Tr/J"

    # Von Mises for combined
    if sigma_x_MPa or sigma_y_MPa or tau_xy_MPa:
        vm = von_mises_stress(
            sigma_x_MPa * 1e6, sigma_y_MPa * 1e6, tau_xy_MPa * 1e6
        )
        vm_MPa = vm / 1e6
        if fos is None:
            fos = sigma_y / vm if vm != 0 else float("inf")
            sigma = vm
        formula = "σ_vm = √(σx²-σxσy+σy²+3τxy²)"
        failure_mode = "Von Mises yielding (combined)"

    stress_MPa = abs(sigma) / 1e6
    safe = fos >= 1.5 if fos is not None else True  # FoS < 1.5 = marginal

    return StressResult(
        stress_MPa=round(stress_MPa, 4),
        strain=round(strain, 8) if strain else None,
        factor_of_safety=round(fos, 3) if fos and fos != float("inf") else fos,
        von_mises_MPa=round(vm_MPa, 4) if vm_MPa else None,
        failure_mode=failure_mode,
        safe=safe,
        formula_used=formula,
    )
