"""
Moment of Inertia Calculator
Covers common engineering cross-sections:
Rectangle, Circle, Hollow Circle, I-Section (H-beam), T-Section, L-Angle
"""

import math
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SectionType(Enum):
    RECTANGLE = "rectangle"
    SOLID_CIRCLE = "solid_circle"
    HOLLOW_CIRCLE = "hollow_circle"
    I_SECTION = "i_section"
    T_SECTION = "t_section"
    L_ANGLE = "l_angle"
    TRIANGLE = "triangle"


@dataclass
class SectionProperties:
    section_type: str
    area_m2: float
    Ixx_m4: float          # Second moment of area about x-x (horizontal) axis
    Iyy_m4: float          # Second moment of area about y-y (vertical) axis
    J_m4: float            # Polar moment of inertia
    radius_gyration_x: float  # r_x = sqrt(Ixx/A)
    radius_gyration_y: float  # r_y = sqrt(Iyy/A)
    centroid_y_m: float    # Distance from bottom to centroid
    section_modulus_x_m3: float  # Sx = Ixx / y_max
    section_modulus_y_m3: float  # Sy = Iyy / x_max


def rectangle(width_m: float, height_m: float) -> SectionProperties:
    """Solid rectangular section"""
    b, h = width_m, height_m
    A = b * h
    Ixx = (b * h**3) / 12
    Iyy = (h * b**3) / 12
    J = Ixx + Iyy
    return SectionProperties(
        section_type="Rectangle",
        area_m2=A,
        Ixx_m4=Ixx,
        Iyy_m4=Iyy,
        J_m4=J,
        radius_gyration_x=math.sqrt(Ixx / A),
        radius_gyration_y=math.sqrt(Iyy / A),
        centroid_y_m=h / 2,
        section_modulus_x_m3=Ixx / (h / 2),
        section_modulus_y_m3=Iyy / (b / 2),
    )


def solid_circle(diameter_m: float) -> SectionProperties:
    """Solid circular section"""
    d = diameter_m
    r = d / 2
    A = math.pi * r**2
    Ixx = (math.pi * d**4) / 64
    Iyy = Ixx
    J = (math.pi * d**4) / 32
    return SectionProperties(
        section_type="Solid Circle",
        area_m2=A,
        Ixx_m4=Ixx,
        Iyy_m4=Iyy,
        J_m4=J,
        radius_gyration_x=math.sqrt(Ixx / A),
        radius_gyration_y=math.sqrt(Iyy / A),
        centroid_y_m=r,
        section_modulus_x_m3=Ixx / r,
        section_modulus_y_m3=Iyy / r,
    )


def hollow_circle(outer_diameter_m: float, inner_diameter_m: float) -> SectionProperties:
    """Hollow circular / tubular section"""
    D, d = outer_diameter_m, inner_diameter_m
    if d >= D:
        raise ValueError("Inner diameter must be less than outer diameter")
    A = math.pi * (D**2 - d**2) / 4
    Ixx = (math.pi / 64) * (D**4 - d**4)
    Iyy = Ixx
    J = (math.pi / 32) * (D**4 - d**4)
    r_outer = D / 2
    return SectionProperties(
        section_type="Hollow Circle (Tube)",
        area_m2=A,
        Ixx_m4=Ixx,
        Iyy_m4=Iyy,
        J_m4=J,
        radius_gyration_x=math.sqrt(Ixx / A),
        radius_gyration_y=math.sqrt(Iyy / A),
        centroid_y_m=r_outer,
        section_modulus_x_m3=Ixx / r_outer,
        section_modulus_y_m3=Iyy / r_outer,
    )


def i_section(
    flange_width_m: float,
    flange_thickness_m: float,
    web_height_m: float,
    web_thickness_m: float,
) -> SectionProperties:
    """
    I-Section (H-beam, W-shape)
    Using parallel axis theorem: I_total = I_flanges + I_web
    """
    bf, tf = flange_width_m, flange_thickness_m
    hw, tw = web_height_m, web_thickness_m
    H = hw + 2 * tf  # total height

    A = 2 * bf * tf + hw * tw

    # I-xx about centroid (symmetric, so centroid is at H/2)
    # Two flanges + web using parallel axis theorem
    I_flange_own = (bf * tf**3) / 12
    d_flange = (hw / 2 + tf / 2)  # distance from centroid to flange centroid
    I_flanges = 2 * (I_flange_own + bf * tf * d_flange**2)
    I_web = (tw * hw**3) / 12
    Ixx = I_flanges + I_web

    # I-yy: flanges dominate
    Iyy = 2 * (tf * bf**3) / 12 + (hw * tw**3) / 12

    J = Ixx + Iyy

    return SectionProperties(
        section_type="I-Section (H-Beam)",
        area_m2=A,
        Ixx_m4=Ixx,
        Iyy_m4=Iyy,
        J_m4=J,
        radius_gyration_x=math.sqrt(Ixx / A),
        radius_gyration_y=math.sqrt(Iyy / A),
        centroid_y_m=H / 2,
        section_modulus_x_m3=Ixx / (H / 2),
        section_modulus_y_m3=Iyy / (bf / 2),
    )


def t_section(
    flange_width_m: float,
    flange_thickness_m: float,
    web_height_m: float,
    web_thickness_m: float,
) -> SectionProperties:
    """
    T-Section — centroid is NOT at mid-height, so we find it first.
    """
    bf, tf = flange_width_m, flange_thickness_m
    hw, tw = web_height_m, web_thickness_m
    H = hw + tf

    A_flange = bf * tf
    A_web = hw * tw
    A = A_flange + A_web

    # Centroid from bottom
    y_bar = (A_flange * (hw + tf / 2) + A_web * hw / 2) / A

    # Parallel axis theorem
    Ixx_flange = (bf * tf**3) / 12 + A_flange * (hw + tf / 2 - y_bar) ** 2
    Ixx_web = (tw * hw**3) / 12 + A_web * (hw / 2 - y_bar) ** 2
    Ixx = Ixx_flange + Ixx_web

    Iyy = (tf * bf**3) / 12 + (hw * tw**3) / 12

    J = Ixx + Iyy
    y_max = max(y_bar, H - y_bar)

    return SectionProperties(
        section_type="T-Section",
        area_m2=A,
        Ixx_m4=Ixx,
        Iyy_m4=Iyy,
        J_m4=J,
        radius_gyration_x=math.sqrt(Ixx / A),
        radius_gyration_y=math.sqrt(Iyy / A),
        centroid_y_m=y_bar,
        section_modulus_x_m3=Ixx / y_max,
        section_modulus_y_m3=Iyy / (max(bf, tw) / 2),
    )


def triangle(base_m: float, height_m: float) -> SectionProperties:
    """Solid triangle — centroid at h/3 from base"""
    b, h = base_m, height_m
    A = 0.5 * b * h
    Ixx = (b * h**3) / 36  # About centroidal axis
    Iyy = (h * b**3) / 48
    J = Ixx + Iyy
    centroid_y = h / 3
    return SectionProperties(
        section_type="Triangle",
        area_m2=A,
        Ixx_m4=Ixx,
        Iyy_m4=Iyy,
        J_m4=J,
        radius_gyration_x=math.sqrt(Ixx / A),
        radius_gyration_y=math.sqrt(Iyy / A),
        centroid_y_m=centroid_y,
        section_modulus_x_m3=Ixx / (2 * h / 3),  # y_max = 2h/3 from centroid
        section_modulus_y_m3=Iyy / (b / 2),
    )


def calculate_section(section_type: SectionType, **kwargs) -> SectionProperties:
    """
    Dispatcher for section calculations.
    Pass keyword args matching the specific section function.
    """
    dispatch = {
        SectionType.RECTANGLE: rectangle,
        SectionType.SOLID_CIRCLE: solid_circle,
        SectionType.HOLLOW_CIRCLE: hollow_circle,
        SectionType.I_SECTION: i_section,
        SectionType.T_SECTION: t_section,
        SectionType.TRIANGLE: triangle,
    }
    func = dispatch.get(section_type)
    if not func:
        raise ValueError(f"Unsupported section type: {section_type}")
    return func(**kwargs)
