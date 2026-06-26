"""
Engineering Unit Converter
Covers: Force, Pressure/Stress, Length, Mass, Temperature,
        Energy, Power, Angle, Area, Volume, Moment/Torque
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ConversionResult:
    from_value: float
    from_unit: str
    to_value: float
    to_unit: str
    category: str
    conversion_factor: float


# ── Conversion tables (all relative to SI base unit) ──────────────────────────

CONVERSIONS: Dict[str, Dict[str, float]] = {
    "force": {
        "N": 1.0,
        "kN": 1e3,
        "MN": 1e6,
        "lbf": 4.44822,
        "kip": 4448.22,
        "tonf": 9806.65,      # metric ton-force
        "dyn": 1e-5,
        "kgf": 9.80665,
    },
    "pressure": {
        "Pa": 1.0,
        "kPa": 1e3,
        "MPa": 1e6,
        "GPa": 1e9,
        "bar": 1e5,
        "atm": 101325.0,
        "psi": 6894.76,
        "ksi": 6.89476e6,
        "mmHg": 133.322,
        "inHg": 3386.39,
        "torr": 133.322,
    },
    "length": {
        "m": 1.0,
        "mm": 1e-3,
        "cm": 1e-2,
        "km": 1e3,
        "in": 0.0254,
        "ft": 0.3048,
        "yd": 0.9144,
        "mi": 1609.344,
        "um": 1e-6,   # micron
        "nm": 1e-9,
    },
    "mass": {
        "kg": 1.0,
        "g": 1e-3,
        "mg": 1e-6,
        "tonne": 1e3,
        "lb": 0.453592,
        "oz": 0.0283495,
        "ton_us": 907.185,   # US short ton
        "ton_uk": 1016.05,   # UK long ton
        "slug": 14.5939,
    },
    "temperature": {
        "C": "celsius",
        "F": "fahrenheit",
        "K": "kelvin",
        "R": "rankine",
    },
    "energy": {
        "J": 1.0,
        "kJ": 1e3,
        "MJ": 1e6,
        "Wh": 3600.0,
        "kWh": 3.6e6,
        "cal": 4.18400,
        "kcal": 4184.0,
        "BTU": 1055.06,
        "ft_lbf": 1.35582,
        "eV": 1.60218e-19,
    },
    "power": {
        "W": 1.0,
        "kW": 1e3,
        "MW": 1e6,
        "hp": 745.7,          # mechanical horsepower
        "hp_m": 735.499,      # metric horsepower
        "BTU_hr": 0.293071,
        "ft_lbf_s": 1.35582,
    },
    "angle": {
        "rad": 1.0,
        "deg": 0.0174533,
        "grad": 0.015708,
        "rev": 6.28318,
        "arcmin": 2.90888e-4,
        "arcsec": 4.84814e-6,
    },
    "area": {
        "m2": 1.0,
        "mm2": 1e-6,
        "cm2": 1e-4,
        "km2": 1e6,
        "in2": 6.4516e-4,
        "ft2": 0.092903,
        "yd2": 0.836127,
        "acre": 4046.86,
        "ha": 1e4,
    },
    "volume": {
        "m3": 1.0,
        "L": 1e-3,
        "mL": 1e-6,
        "cm3": 1e-6,
        "in3": 1.6387e-5,
        "ft3": 0.0283168,
        "gal_us": 3.78541e-3,
        "gal_uk": 4.54609e-3,
        "bbl": 0.158987,
    },
    "torque": {
        "Nm": 1.0,
        "kNm": 1e3,
        "MNm": 1e6,
        "Ncm": 0.01,
        "lbf_ft": 1.35582,
        "lbf_in": 0.112985,
        "kgf_m": 9.80665,
    },
}


# ── Temperature conversion (special case — not multiplicative) ─────────────────

def _convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Convert between C, F, K, R"""
    # First to Kelvin
    to_K = {
        "C": lambda v: v + 273.15,
        "F": lambda v: (v + 459.67) * 5 / 9,
        "K": lambda v: v,
        "R": lambda v: v * 5 / 9,
    }
    from_K = {
        "C": lambda v: v - 273.15,
        "F": lambda v: v * 9 / 5 - 459.67,
        "K": lambda v: v,
        "R": lambda v: v * 9 / 5,
    }
    K = to_K[from_unit](value)
    return from_K[to_unit](K)


# ── Main converter ─────────────────────────────────────────────────────────────

def convert(
    value: float,
    from_unit: str,
    to_unit: str,
    category: Optional[str] = None,
) -> ConversionResult:
    """
    Convert a value between engineering units.

    Args:
        value: Numeric value to convert
        from_unit: Source unit string (e.g., 'MPa', 'in', 'kN')
        to_unit: Target unit string
        category: Optional category hint ('force', 'pressure', etc.)

    Returns:
        ConversionResult with the converted value and metadata
    """
    from_unit = from_unit.strip()
    to_unit = to_unit.strip()

    if from_unit == to_unit:
        return ConversionResult(value, from_unit, value, to_unit, "same", 1.0)

    # Detect category
    found_category = None
    if category:
        if category in CONVERSIONS:
            found_category = category
    else:
        for cat, units in CONVERSIONS.items():
            if from_unit in units and to_unit in units:
                found_category = cat
                break

    if not found_category:
        raise ValueError(
            f"Cannot find category for '{from_unit}' → '{to_unit}'. "
            f"Ensure both units belong to the same category."
        )

    if found_category == "temperature":
        result = _convert_temperature(value, from_unit, to_unit)
        factor = result / value if value != 0 else 0.0
        return ConversionResult(value, from_unit, round(result, 6), to_unit, "temperature", factor)

    units = CONVERSIONS[found_category]
    if from_unit not in units:
        raise ValueError(f"Unknown unit '{from_unit}' in category '{found_category}'")
    if to_unit not in units:
        raise ValueError(f"Unknown unit '{to_unit}' in category '{found_category}'")

    factor_from = units[from_unit]
    factor_to = units[to_unit]
    conversion_factor = factor_from / factor_to
    result = value * conversion_factor

    return ConversionResult(
        from_value=value,
        from_unit=from_unit,
        to_value=round(result, 8),
        to_unit=to_unit,
        category=found_category,
        conversion_factor=round(conversion_factor, 8),
    )


def list_units(category: str) -> list:
    """List all available units for a given category."""
    if category not in CONVERSIONS:
        raise ValueError(f"Unknown category '{category}'. Available: {list(CONVERSIONS.keys())}")
    return list(CONVERSIONS[category].keys())


def available_categories() -> list:
    """Return all supported conversion categories."""
    return list(CONVERSIONS.keys())
