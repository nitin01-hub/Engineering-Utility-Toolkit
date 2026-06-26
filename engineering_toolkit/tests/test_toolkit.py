"""
Unit Tests — Engineering Calculator Toolkit
Run: python -m pytest tests/ -v
"""

import math
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.beam import calculate_beam_deflection, BeamType, LoadType
from core.stress import calculate_stress, StressType, von_mises_stress
from core.inertia import rectangle, solid_circle, hollow_circle, i_section, t_section
from core.units import convert, available_categories, list_units


# ── Beam Deflection Tests ──────────────────────────────────────────────────────

class TestBeamDeflection:

    def test_simply_supported_point_load_centre(self):
        """PL³/48EI — classic formula"""
        res = calculate_beam_deflection(
            BeamType.SIMPLY_SUPPORTED, LoadType.POINT_LOAD,
            length_m=4.0, load_N=10000,
            elastic_modulus_GPa=200, moment_of_inertia_m4=8.33e-6,
        )
        expected = (10000 * 4.0**3) / (48 * 200e9 * 8.33e-6) * 1000  # mm
        assert abs(res.max_deflection_mm - expected) < 0.01

    def test_cantilever_udl(self):
        """wL⁴/8EI"""
        res = calculate_beam_deflection(
            BeamType.CANTILEVER, LoadType.UDL,
            length_m=3.0, load_N=6000,
            elastic_modulus_GPa=200, moment_of_inertia_m4=1e-5,
        )
        w = 6000 / 3.0
        expected = (w * 3.0**4) / (8 * 200e9 * 1e-5) * 1000
        assert abs(res.max_deflection_mm - expected) < 0.01

    def test_fixed_fixed_point_load(self):
        res = calculate_beam_deflection(
            BeamType.FIXED_FIXED, LoadType.POINT_LOAD,
            length_m=5.0, load_N=20000,
            elastic_modulus_GPa=200, moment_of_inertia_m4=5e-5,
        )
        assert res.max_deflection_mm > 0

    def test_deflection_warning_triggered(self):
        """Short span with huge load should trigger L/360 warning"""
        res = calculate_beam_deflection(
            BeamType.SIMPLY_SUPPORTED, LoadType.POINT_LOAD,
            length_m=1.0, load_N=1e7,
            elastic_modulus_GPa=200, moment_of_inertia_m4=1e-8,
        )
        assert res.warning is not None

    def test_simply_supported_udl_shear(self):
        """Shear at support = wL/2"""
        res = calculate_beam_deflection(
            BeamType.SIMPLY_SUPPORTED, LoadType.UDL,
            length_m=4.0, load_N=8000,
            elastic_modulus_GPa=200, moment_of_inertia_m4=1e-5,
        )
        expected_V = 8000 / 2
        assert abs(res.max_shear_force_N - expected_V) < 1.0


# ── Stress Tests ───────────────────────────────────────────────────────────────

class TestStress:

    def test_normal_stress_basic(self):
        """σ = F/A = 50kN / 200cm² = 25 MPa"""
        res = calculate_stress(
            StressType.NORMAL,
            yield_strength_MPa=250,
            force_N=50000, area_m2=0.002,
        )
        assert abs(res.stress_MPa - 25.0) < 0.01

    def test_factor_of_safety_safe(self):
        """FoS should be ≥ 1.5 for safe design"""
        res = calculate_stress(
            StressType.NORMAL,
            yield_strength_MPa=250,
            force_N=50000, area_m2=0.002,
        )
        assert res.safe is True
        assert res.factor_of_safety >= 1.5

    def test_factor_of_safety_unsafe(self):
        """Near-yield stress → unsafe"""
        res = calculate_stress(
            StressType.NORMAL,
            yield_strength_MPa=250,
            force_N=400000, area_m2=0.002,  # σ = 200 MPa, FoS = 1.25 < 1.5
        )
        assert res.safe is False

    def test_bending_stress(self):
        """σ = My/I"""
        M, y, I = 1000, 0.05, 1e-5
        res = calculate_stress(
            StressType.BENDING,
            yield_strength_MPa=300,
            moment_Nm=M, distance_m=y, moment_of_inertia_m4=I,
        )
        expected = (M * y / I) / 1e6
        assert abs(res.stress_MPa - expected) < 0.001

    def test_von_mises_biaxial(self):
        """Von Mises for equal biaxial: σ_vm = σ"""
        vm = von_mises_stress(100e6, 100e6, 0)
        assert abs(vm - 100e6) < 100  # same as uniaxial in equal biax

    def test_shear_tresca(self):
        res = calculate_stress(
            StressType.SHEAR,
            yield_strength_MPa=250,
            shear_force_N=20000, area_m2=0.001,
        )
        assert res.stress_MPa > 0
        assert "Tresca" in res.failure_mode


# ── Moment of Inertia Tests ────────────────────────────────────────────────────

class TestInertia:

    def test_rectangle_Ixx(self):
        """Ixx = bh³/12"""
        res = rectangle(0.1, 0.2)
        expected = (0.1 * 0.2**3) / 12
        assert abs(res.Ixx_m4 - expected) < 1e-12

    def test_rectangle_area(self):
        res = rectangle(0.05, 0.10)
        assert abs(res.area_m2 - 0.005) < 1e-10

    def test_solid_circle_Ixx(self):
        """Ixx = πd⁴/64"""
        d = 0.1
        res = solid_circle(d)
        expected = math.pi * d**4 / 64
        assert abs(res.Ixx_m4 - expected) < 1e-15

    def test_hollow_circle_area(self):
        D, d = 0.12, 0.10
        res = hollow_circle(D, d)
        expected = math.pi * (D**2 - d**2) / 4
        assert abs(res.area_m2 - expected) < 1e-10

    def test_hollow_circle_bad_input(self):
        with pytest.raises(ValueError):
            hollow_circle(0.05, 0.10)  # inner > outer

    def test_i_section_symmetry(self):
        """Symmetric I-beam: centroid at H/2"""
        res = i_section(0.15, 0.012, 0.25, 0.008)
        H = 0.25 + 2 * 0.012
        assert abs(res.centroid_y_m - H / 2) < 1e-9

    def test_section_modulus_positive(self):
        res = rectangle(0.1, 0.2)
        assert res.section_modulus_x_m3 > 0
        assert res.section_modulus_y_m3 > 0

    def test_t_section_centroid_asymmetry(self):
        """T-section centroid should NOT be at mid-height"""
        res = t_section(0.12, 0.01, 0.20, 0.008)
        H = 0.20 + 0.01
        assert abs(res.centroid_y_m - H / 2) > 1e-4  # it's off-centre


# ── Unit Converter Tests ───────────────────────────────────────────────────────

class TestUnits:

    def test_force_N_to_kN(self):
        res = convert(1000, "N", "kN")
        assert abs(res.to_value - 1.0) < 1e-6

    def test_pressure_MPa_to_psi(self):
        res = convert(1, "MPa", "psi")
        assert abs(res.to_value - 145.038) < 0.01

    def test_length_m_to_ft(self):
        res = convert(1, "m", "ft")
        assert abs(res.to_value - 3.28084) < 0.001

    def test_temperature_C_to_F(self):
        res = convert(100, "C", "F")
        assert abs(res.to_value - 212.0) < 0.01

    def test_temperature_C_to_K(self):
        res = convert(0, "C", "K")
        assert abs(res.to_value - 273.15) < 0.01

    def test_same_unit(self):
        res = convert(42, "MPa", "MPa")
        assert res.to_value == 42

    def test_invalid_cross_category(self):
        with pytest.raises(ValueError):
            convert(1, "N", "MPa")  # different categories

    def test_available_categories_not_empty(self):
        cats = available_categories()
        assert len(cats) > 0
        assert "force" in cats
        assert "pressure" in cats

    def test_list_units_force(self):
        units = list_units("force")
        assert "N" in units
        assert "kN" in units
        assert "lbf" in units

    def test_energy_J_to_kWh(self):
        res = convert(3.6e6, "J", "kWh")
        assert abs(res.to_value - 1.0) < 1e-5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
