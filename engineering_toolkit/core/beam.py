"""
Beam Deflection Calculator
Supports Simply Supported, Cantilever, and Fixed-Fixed beams
under Point Load or Uniformly Distributed Load (UDL)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class BeamType(Enum):
    SIMPLY_SUPPORTED = "simply_supported"
    CANTILEVER = "cantilever"
    FIXED_FIXED = "fixed_fixed"


class LoadType(Enum):
    POINT_LOAD = "point_load"
    UDL = "udl"  # Uniformly Distributed Load


@dataclass
class BeamResult:
    max_deflection_mm: float
    max_bending_moment_Nm: float
    max_shear_force_N: float
    deflection_location: str
    formula_used: str
    warning: Optional[str] = None


def calculate_beam_deflection(
    beam_type: BeamType,
    load_type: LoadType,
    length_m: float,
    load_N: float,
    elastic_modulus_GPa: float,
    moment_of_inertia_m4: float,
    load_position_ratio: float = 0.5,  # a/L for point load (0 to 1)
) -> BeamResult:
    """
    Calculate beam deflection, bending moment, and shear force.

    Args:
        beam_type: Type of beam support
        load_type: Type of loading
        length_m: Beam length in meters
        load_N: Load in Newtons (total for UDL, point for point load)
        elastic_modulus_GPa: Young's modulus in GPa (e.g., 200 for steel)
        moment_of_inertia_m4: Second moment of area in m^4
        load_position_ratio: Position of point load as fraction of length (0-1)

    Returns:
        BeamResult with deflection, bending moment, shear force
    """
    L = length_m
    E = elastic_modulus_GPa * 1e9  # Convert GPa to Pa
    I = moment_of_inertia_m4
    P = load_N
    EI = E * I

    warning = None

    if load_type == LoadType.POINT_LOAD:
        a = load_position_ratio * L
        b = L - a

        if beam_type == BeamType.SIMPLY_SUPPORTED:
            # Max deflection at x = a when a > L/2, else at centre approx.
            # Exact: delta_max = P*a*b*(a+2b)*sqrt(3a(a+2b)) / (27*E*I*L) when a <= L/2
            # For midpoint load: delta = PL^3 / 48EI
            if abs(a - L / 2) < 1e-6:
                delta = (P * L**3) / (48 * EI)
                M_max = P * L / 4
                formula = "δ = PL³/48EI (central point load)"
            else:
                # General case — exact formula
                delta = (P * a**2 * b**2) / (3 * EI * L)
                M_max = (P * a * b) / L
                formula = "δ = Pa²b²/3EIL (off-centre point load)"
            V_max = P * b / L if a <= L / 2 else P * a / L

        elif beam_type == BeamType.CANTILEVER:
            # Load at free end (a = L) is the worst case
            a = load_position_ratio * L  # distance from fixed end
            delta = (P * a**3) / (3 * EI)
            M_max = P * a  # at fixed end
            V_max = P
            formula = "δ = Pa³/3EI (cantilever, point load at distance a)"

        elif beam_type == BeamType.FIXED_FIXED:
            delta = (P * a**3 * b**3) / (3 * EI * L**3)
            M_max = (P * a * b**2) / L**2
            V_max = (P * b**2 * (3 * a + b)) / L**3
            formula = "δ = Pa³b³/3EIL³ (fixed-fixed, point load)"

    elif load_type == LoadType.UDL:
        w = P / L  # load per unit length (N/m)

        if beam_type == BeamType.SIMPLY_SUPPORTED:
            delta = (5 * w * L**4) / (384 * EI)
            M_max = (w * L**2) / 8
            V_max = (w * L) / 2
            formula = "δ = 5wL⁴/384EI (UDL, simply supported)"

        elif beam_type == BeamType.CANTILEVER:
            delta = (w * L**4) / (8 * EI)
            M_max = (w * L**2) / 2
            V_max = w * L
            formula = "δ = wL⁴/8EI (UDL, cantilever)"

        elif beam_type == BeamType.FIXED_FIXED:
            delta = (w * L**4) / (384 * EI)
            M_max = (w * L**2) / 12
            V_max = (w * L) / 2
            formula = "δ = wL⁴/384EI (UDL, fixed-fixed)"

    # Deflection limit check (L/360 is a common serviceability limit)
    limit = L / 360
    if delta > limit:
        warning = f"Deflection {delta*1000:.2f} mm exceeds serviceability limit L/360 = {limit*1000:.2f} mm"

    location_map = {
        BeamType.SIMPLY_SUPPORTED: "at mid-span",
        BeamType.CANTILEVER: "at free end",
        BeamType.FIXED_FIXED: "at mid-span",
    }

    return BeamResult(
        max_deflection_mm=delta * 1000,
        max_bending_moment_Nm=M_max,
        max_shear_force_N=V_max,
        deflection_location=location_map[beam_type],
        formula_used=formula,
        warning=warning,
    )
