<div align="center">

# ⚙️ Engineering Calculator Toolkit

**A Python engineering utility tool with a dark-themed interactive GUI**

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/UI-Tkinter-FF6B35?style=for-the-badge)
![Tests](https://img.shields.io/badge/Tests-25%20Passing-22C55E?style=for-the-badge)
![Dependencies](https://img.shields.io/badge/Dependencies-Zero%20(stdlib)-A855F7?style=for-the-badge)

*Beam Deflection · Stress & FoS · Moment of Inertia · Unit Converter*

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [Modules](#-modules)
  - [Beam Deflection](#1--beam-deflection)
  - [Stress & Factor of Safety](#2--stress--factor-of-safety)
  - [Moment of Inertia](#3--moment-of-inertia)
  - [Unit Converter](#4--unit-converter)
- [Engineering Concepts](#-engineering-concepts-applied)
- [Key Design Decisions](#-key-design-decisions)
- [Dependencies](#-dependencies)
- [Extending the Toolkit](#-extending-the-toolkit)

---

## 🔍 Overview

A modular Python toolkit for structural and mechanical engineering calculations. The core logic is completely separated from the UI layer — making it easy to use as a library, a GUI app, or a CLI tool.

```
GUI  ──►  ui/app.py  ──►  core/  ──►  beam.py
CLI  ──►  main.py    ──►  core/  ──►  stress.py
API  ──►  import     ──►  core/  ──►  inertia.py
                                  ──►  units.py
```

---

## 📁 Project Structure

```
engineering_toolkit/
│
├── main.py                  ← Entry point (GUI / CLI / Tests)
├── requirements.txt
│
├── core/                    ← Pure logic, zero UI dependency
│   ├── __init__.py
│   ├── beam.py              ← Beam deflection (SS, Cantilever, Fixed-Fixed)
│   ├── stress.py            ← Stress, strain, Von Mises, FoS
│   ├── inertia.py           ← Section properties (Ixx, Iyy, J, Sx, Sy)
│   └── units.py             ← 10-category, 80+ unit converter
│
├── ui/
│   └── app.py               ← Tkinter GUI — 4 tabbed calculators
│
└── tests/
    └── test_toolkit.py      ← 25 unit tests (pytest)
```

---

## 🚀 Quick Start

> **macOS / Linux** — use `python3` and `pip3` instead of `python` and `pip`

### Launch the GUI
```bash
cd engineering_toolkit
python3 main.py
```

### CLI interactive mode
```bash
python3 main.py --cli
```

### Run tests
```bash
pip3 install pytest
python3 -m pytest tests/ -v

# or via the launcher
python3 main.py --test
```

---

## 📐 Modules

### 1 · Beam Deflection
> `core/beam.py`

Calculates maximum deflection, bending moment, and shear force.

| Beam Type | Point Load Formula | UDL Formula |
|---|---|---|
| Simply Supported | `δ = PL³/48EI` (centre) | `δ = 5wL⁴/384EI` |
| Cantilever | `δ = Pa³/3EI` | `δ = wL⁴/8EI` |
| Fixed-Fixed | `δ = Pa³b³/3EIL³` | `δ = wL⁴/384EI` |

**Outputs**
- Max deflection (mm) + formula used
- Max bending moment (N·m)
- Max shear force (N)
- ⚠️ L/360 serviceability warning if exceeded

**Example**
```python
from core import calculate_beam_deflection, BeamType, LoadType

result = calculate_beam_deflection(
    beam_type=BeamType.SIMPLY_SUPPORTED,
    load_type=LoadType.POINT_LOAD,
    length_m=4.0,
    load_N=10000,
    elastic_modulus_GPa=200,
    moment_of_inertia_m4=8.33e-6,
)

print(result.max_deflection_mm)      # → 4.0065 mm
print(result.max_bending_moment_Nm)  # → 10000.0 N·m
print(result.warning)                # → None (within L/360)
```

---

### 2 · Stress & Factor of Safety
> `core/stress.py`

| Stress Type | Formula | Failure Criterion |
|---|---|---|
| Normal (axial) | `σ = F/A` | Yielding |
| Bending | `σ = My/I` | Flexural yielding |
| Shear | `τ = V/A` | Tresca (`τ_y = σ_y/2`) |
| Torsional | `τ = Tr/J` | Torsional shear yielding |
| Combined | Von Mises | `σ_vm = √(σx²−σxσy+σy²+3τxy²)` |
| Thermal | `σ = E·α·ΔT` | Constrained expansion |

**Safety check** — FoS ≥ 1.5 → ✅ SAFE · FoS < 1.5 → ❌ UNSAFE

**Example**
```python
from core import calculate_stress, StressType

result = calculate_stress(
    stress_type=StressType.NORMAL,
    yield_strength_MPa=250,
    force_N=50000,
    area_m2=0.002,
)

print(result.stress_MPa)         # → 25.0 MPa
print(result.factor_of_safety)   # → 10.0
print(result.safe)               # → True
print(result.failure_mode)       # → "Yielding (tensile)"
```

---

### 3 · Moment of Inertia
> `core/inertia.py`

Full section properties using exact formulas + parallel axis theorem for composite sections.

| Section | Ixx | Notes |
|---|---|---|
| Rectangle | `bh³/12` | — |
| Solid Circle | `πd⁴/64` | — |
| Hollow Circle | `π(D⁴−d⁴)/64` | Tube / pipe |
| I-Section | Parallel axis theorem | Flanges + web |
| T-Section | Parallel axis theorem | Centroid computed first (asymmetric) |
| Triangle | `bh³/36` | About centroidal axis |

**Outputs per section**

```
Area (m²)          Centroid from base
Ixx, Iyy (m⁴)     Second moment of area
J (m⁴)            Polar moment of inertia
Sx, Sy (m³)       Section modulus
rx, ry (mm)       Radius of gyration
```

**Example**
```python
from core import calculate_section, SectionType

result = calculate_section(
    SectionType.I_SECTION,
    flange_width_m=0.15,
    flange_thickness_m=0.012,
    web_height_m=0.25,
    web_thickness_m=0.008,
)

print(f"Ixx = {result.Ixx_m4:.4e} m⁴")
print(f"Sx  = {result.section_modulus_x_m3:.4e} m³")
```

---

### 4 · Unit Converter
> `core/units.py`

| Category | Units |
|---|---|
| Force | N, kN, MN, lbf, kip, kgf, tonf |
| Pressure | Pa, kPa, MPa, GPa, bar, atm, psi, ksi |
| Length | m, mm, cm, km, in, ft, yd, mi, μm |
| Mass | kg, g, tonne, lb, oz, slug |
| Temperature | °C, °F, K, °R |
| Energy | J, kJ, kWh, cal, BTU |
| Power | W, kW, MW, hp |
| Angle | rad, deg, grad, arcmin |
| Area | m², mm², cm², in², ft², ha |
| Torque | N·m, kN·m, lbf·ft, kgf·m |

**Example**
```python
from core import convert

r = convert(1, "MPa", "psi")
print(f"{r.from_value} {r.from_unit} = {r.to_value} {r.to_unit}")
# → 1 MPa = 145.038 psi

r2 = convert(100, "C", "F")
print(r2.to_value)  # → 212.0
```

---

## 🧠 Engineering Concepts Applied

| Concept | Implementation |
|---|---|
| **Numerical Computation** | Deflection integrals (`PL³/48EI`), parallel axis theorem (`I = I₀ + Ad²`), Von Mises tensor |
| **Formula Modelling** | Python `Enum` dispatch selects the exact textbook formula at runtime |
| **Scientific Scripting** | `dataclasses` for structured results, type hints, SI as the canonical unit base |
| **Engineering Logic Translation** | L/360 serviceability limit, Tresca criterion (`τ_y = σ_y/2`), FoS < 1.5 flagged unsafe |

---

## 🏗️ Key Design Decisions

### Core / UI separation
`core/` has zero Tkinter dependency. Every function takes plain numbers and returns a dataclass. Swap the GUI for Flask or FastAPI without touching a single formula.

### Enum-driven formula dispatch
`BeamType` and `LoadType` are Python `Enum`s — not strings. This makes invalid types impossible and gives full IDE autocomplete.

```python
# ✅ Correct — enum-safe, autocomplete works
BeamType.SIMPLY_SUPPORTED

# ❌ Fragile — typo-prone, no autocomplete
"simply_supported"
```

### Dataclass return types
All calculators return structured dataclasses so the UI can access `.factor_of_safety` or `.warning` directly — no string parsing needed.

### T-section centroid first
Unlike symmetric sections, a T-section centroid is not at mid-height. The code computes it via the composite area method before applying the parallel axis theorem — a step students commonly miss.

---

## 📦 Dependencies

| Usage | Requirement |
|---|---|
| Core calculations | Python 3.8+ stdlib (`math`, `dataclasses`, `enum`) |
| GUI | Python 3.8+ stdlib (`tkinter`) |
| Tests | `pytest` — `pip3 install pytest` |

**No third-party packages required for the core or UI.**

---

## 🔧 Extending the Toolkit

### Add a new cross-section
1. Write a function in `core/inertia.py`
2. Add an entry to the `SectionType` enum
3. Add to the `dispatch` dict in `calculate_section()`
4. Add UI fields in `InertiaTab._update_fields()` in `ui/app.py`

### Add a new unit category
1. Add a new dict entry to `CONVERSIONS` in `core/units.py`
2. The converter and UI pick it up automatically — no other changes needed

---

<div align="center">

Made with Python

</div>

<img width="1152" height="648" alt="Engineering_toolkit" src="https://github.com/user-attachments/assets/2f53c66c-6b8c-45a5-b0e8-fb529ff346e3" />


