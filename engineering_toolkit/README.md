# ⚙ Engineering Calculator Toolkit

A Python engineering utility tool featuring a dark-themed interactive GUI and clean modular core.

## Project Structure

```
engineering_toolkit/
│
├── main.py                  ← Entry point (GUI / CLI / Tests)
├── requirements.txt
│
├── core/                    ← Pure logic, no UI dependency
│   ├── __init__.py
│   ├── beam.py              ← Beam deflection (SS, Cantilever, Fixed-Fixed)
│   ├── stress.py            ← Stress, strain, Von Mises, FoS
│   ├── inertia.py           ← Section properties (Ixx, Iyy, J, Sx, Sy)
│   └── units.py             ← 10-category unit converter
│
├── ui/
│   └── app.py               ← Tkinter GUI (4 tabbed calculators)
│
└── tests/
    └── test_toolkit.py      ← 25+ unit tests (pytest)
```

## Quick Start

```bash
# Launch GUI
python main.py

# CLI interactive mode
python main.py --cli

# Run tests
python main.py --test
# or
python -m pytest tests/ -v
```

## Features

### 1. Beam Deflection (`core/beam.py`)
- Simply Supported, Cantilever, Fixed-Fixed beams
- Point Load and UDL (Uniformly Distributed Load)
- Outputs: max deflection (mm), bending moment (N·m), shear force (N)
- L/360 serviceability check with warning

### 2. Stress & Factor of Safety (`core/stress.py`)
- Normal (axial), Bending (flexural), Shear, Torsional
- Von Mises equivalent stress for combined loading
- Tresca criterion for shear failure
- Thermal stress calculation
- FoS ≥ 1.5 safety check

### 3. Moment of Inertia (`core/inertia.py`)
- Rectangle, Solid Circle, Hollow Circle (tube)
- I-Section (H-Beam), T-Section, Triangle
- Outputs: Area, Ixx, Iyy, J (polar), Section Modulus (Sx, Sy), Radius of Gyration

### 4. Unit Converter (`core/units.py`)
- 10 categories: Force, Pressure, Length, Mass, Temperature,
  Energy, Power, Angle, Area, Volume, Torque
- 80+ units total

## Key Concepts Applied

| Concept | Where |
|---|---|
| Numerical Computation | Beam deflection integrals, parallel axis theorem |
| Formula Modelling | Enum-driven formula dispatch in beam.py |
| Scientific Scripting | Dataclasses, type hints, structured output |
| Engineering Logic Translation | FoS checks, L/360 serviceability, Tresca criterion |

## Dependencies

- **Core + GUI**: Python 3.8+ stdlib only (math, tkinter, dataclasses, enum)
- **Tests**: `pytest` (`pip install pytest`)

## Extending

To add a new section type:
1. Add a function in `core/inertia.py`
2. Add an entry to `SectionType` enum
3. Add to `dispatch` dict in `calculate_section()`
4. Add UI fields in `InertiaTab._update_fields()` in `ui/app.py`
