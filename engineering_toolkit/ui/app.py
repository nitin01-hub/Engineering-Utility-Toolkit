"""
Engineering Calculator Toolkit — Interactive UI
Built with Tkinter (stdlib — no extra installs needed)
Theme: Dark engineering aesthetic with tabbed interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import sys
import os

# Allow running from repo root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import (
    calculate_beam_deflection, BeamType, LoadType,
    calculate_stress, StressType,
    calculate_section, SectionType,
    convert, available_categories, list_units,
)


# ── Color palette ──────────────────────────────────────────────────────────────
DARK   = "#0d1117"
PANEL  = "#161b22"
CARD   = "#1e2530"
BORDER = "#30363d"
BLUE   = "#58a6ff"
GREEN  = "#3fb950"
AMBER  = "#d29922"
RED    = "#f85149"
TEXT   = "#e6edf3"
MUTED  = "#8b949e"
MONO   = "Courier New"


# ── Utility helpers ────────────────────────────────────────────────────────────

def styled_label(parent, text, size=10, color=TEXT, bold=False, mono=False):
    f = (MONO if mono else "Segoe UI", size, "bold" if bold else "normal")
    return tk.Label(parent, text=text, font=f, bg=PANEL, fg=color)


def styled_entry(parent, width=18, textvariable=None):
    e = tk.Entry(
        parent, width=width, bg=CARD, fg=TEXT, insertbackground=BLUE,
        relief="flat", bd=0, font=(MONO, 10),
        highlightthickness=1, highlightbackground=BORDER,
        highlightcolor=BLUE, textvariable=textvariable,
    )
    return e


def styled_combo(parent, values, width=20, textvariable=None):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Eng.TCombobox",
        fieldbackground=CARD, background=CARD, foreground=TEXT,
        selectbackground=BLUE, selectforeground=DARK,
        bordercolor=BORDER, arrowcolor=BLUE,
        font=(MONO, 10),
    )
    c = ttk.Combobox(parent, values=values, width=width, style="Eng.TCombobox",
                     textvariable=textvariable, state="readonly")
    c.set(values[0] if values else "")
    return c


def result_box(parent, height=10):
    """A read-only styled text widget for results."""
    frame = tk.Frame(parent, bg=DARK, bd=1, relief="flat",
                     highlightthickness=1, highlightbackground=BLUE)
    txt = tk.Text(frame, height=height, bg=DARK, fg=GREEN,
                  font=(MONO, 10), bd=0, padx=10, pady=8,
                  relief="flat", state="disabled", wrap="word")
    sb = tk.Scrollbar(frame, command=txt.yview, bg=PANEL, troughcolor=PANEL,
                      width=8)
    txt.configure(yscrollcommand=sb.set)
    txt.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return frame, txt


def write_result(txt_widget, text, tag="normal"):
    txt_widget.configure(state="normal")
    txt_widget.delete("1.0", "end")
    txt_widget.insert("end", text)
    txt_widget.configure(state="disabled")


def section_header(parent, text):
    f = tk.Frame(parent, bg=BLUE, height=2)
    f.pack(fill="x", pady=(14, 4))
    tk.Label(parent, text=text, font=("Segoe UI", 11, "bold"),
             bg=PANEL, fg=BLUE).pack(anchor="w")


# ── Tab 1: Beam Deflection ─────────────────────────────────────────────────────

class BeamTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=PANEL)
        self._build()

    def _build(self):
        section_header(self, "⬡ Beam Deflection Calculator")

        form = tk.Frame(self, bg=PANEL)
        form.pack(fill="x", padx=20, pady=8)

        # Row 0 — beam type & load type
        r = 0
        styled_label(form, "Beam type").grid(row=r, column=0, sticky="w", pady=3)
        self.beam_type = tk.StringVar(value="Simply Supported")
        styled_combo(form, ["Simply Supported", "Cantilever", "Fixed-Fixed"],
                     textvariable=self.beam_type).grid(row=r, column=1, sticky="w", padx=(8,20))

        styled_label(form, "Load type").grid(row=r, column=2, sticky="w", pady=3)
        self.load_type = tk.StringVar(value="Point Load")
        styled_combo(form, ["Point Load", "UDL (Distributed)"],
                     textvariable=self.load_type).grid(row=r, column=3, sticky="w", padx=8)

        fields = [
            ("Length (m)", "3.0"), ("Load (N)", "10000"),
            ("E — Young's Modulus (GPa)", "200"), ("I — Moment of Inertia (m⁴)", "8.33e-6"),
            ("Load position (0–1, for point load)", "0.5"),
        ]
        self.entries = {}
        for i, (label, default) in enumerate(fields):
            r = i + 1
            styled_label(form, label).grid(row=r, column=0, sticky="w", pady=3)
            v = tk.StringVar(value=default)
            e = styled_entry(form, textvariable=v)
            e.grid(row=r, column=1, sticky="w", padx=(8, 20))
            self.entries[label] = v

        # Calculate button
        tk.Button(self, text="▶  Calculate Deflection", font=("Segoe UI", 11, "bold"),
                  bg=BLUE, fg=DARK, activebackground="#79c0ff", relief="flat",
                  padx=20, pady=8, cursor="hand2",
                  command=self._calculate).pack(pady=12)

        frame, self.out = result_box(self, height=11)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    def _calculate(self):
        try:
            beam_map = {
                "Simply Supported": BeamType.SIMPLY_SUPPORTED,
                "Cantilever": BeamType.CANTILEVER,
                "Fixed-Fixed": BeamType.FIXED_FIXED,
            }
            load_map = {"Point Load": LoadType.POINT_LOAD, "UDL (Distributed)": LoadType.UDL}

            L = float(self.entries["Length (m)"].get())
            P = float(self.entries["Load (N)"].get())
            E = float(self.entries["E — Young's Modulus (GPa)"].get())
            I = float(self.entries["I — Moment of Inertia (m⁴)"].get())
            pos = float(self.entries["Load position (0–1, for point load)"].get())

            res = calculate_beam_deflection(
                beam_type=beam_map[self.beam_type.get()],
                load_type=load_map[self.load_type.get()],
                length_m=L, load_N=P,
                elastic_modulus_GPa=E, moment_of_inertia_m4=I,
                load_position_ratio=pos,
            )

            out = f"""{'─'*50}
  BEAM DEFLECTION RESULTS
{'─'*50}
  Beam type     : {self.beam_type.get()}
  Load type     : {self.load_type.get()}
  Length        : {L} m
  Load          : {P:,.0f} N
  EI            : {E * I * 1e9:.4e} N·m²

  Formula used  : {res.formula_used}

  Max Deflection      : {res.max_deflection_mm:.4f} mm  ({res.deflection_location})
  Max Bending Moment  : {res.max_bending_moment_Nm:,.2f} N·m
  Max Shear Force     : {res.max_shear_force_N:,.2f} N
{'─'*50}"""

            if res.warning:
                out += f"\n  ⚠ WARNING: {res.warning}\n{'─'*50}"
            else:
                out += "\n  ✓ Deflection within serviceability limit (L/360)\n" + "─"*50

            write_result(self.out, out)
        except Exception as ex:
            messagebox.showerror("Calculation Error", str(ex))


# ── Tab 2: Stress Calculator ───────────────────────────────────────────────────

class StressTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=PANEL)
        self._build()

    def _build(self):
        section_header(self, "⬡ Stress & Safety Factor Calculator")

        form = tk.Frame(self, bg=PANEL)
        form.pack(fill="x", padx=20, pady=8)

        styled_label(form, "Stress type").grid(row=0, column=0, sticky="w", pady=3)
        self.stype = tk.StringVar(value="Normal (Axial)")
        styled_combo(form, ["Normal (Axial)", "Bending", "Shear", "Torsional"],
                     textvariable=self.stype).grid(row=0, column=1, sticky="w", padx=(8, 20), columnspan=3)

        fields = [
            ("Yield Strength (MPa)", "250"),
            ("Elastic Modulus (GPa)", "200"),
            ("Force / Axial Load (N)", "50000"),
            ("Cross-section Area (m²)", "0.002"),
            ("Bending Moment (N·m)", "0"),
            ("Distance from NA (m)", "0.05"),
            ("Moment of Inertia (m⁴)", "1e-5"),
            ("Shear Force (N)", "0"),
            ("Torque (N·m)", "0"),
            ("Shaft Radius (m)", "0.025"),
            ("Polar Moment J (m⁴)", "1e-7"),
        ]
        self.entries = {}
        for i, (label, default) in enumerate(fields):
            row = i + 1
            col_offset = 0 if i < 6 else 2
            r = i + 1 if i < 6 else i - 5
            styled_label(form, label).grid(row=r, column=col_offset, sticky="w", pady=3)
            v = tk.StringVar(value=default)
            e = styled_entry(form, width=16, textvariable=v)
            e.grid(row=r, column=col_offset + 1, sticky="w", padx=(8, 16))
            self.entries[label] = v

        tk.Button(self, text="▶  Calculate Stress", font=("Segoe UI", 11, "bold"),
                  bg=BLUE, fg=DARK, relief="flat", padx=20, pady=8, cursor="hand2",
                  command=self._calculate).pack(pady=12)

        frame, self.out = result_box(self, height=12)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    def _calculate(self):
        try:
            stype_map = {
                "Normal (Axial)": StressType.NORMAL,
                "Bending": StressType.BENDING,
                "Shear": StressType.SHEAR,
                "Torsional": StressType.TORSIONAL,
            }
            g = lambda k: float(self.entries[k].get())

            res = calculate_stress(
                stress_type=stype_map[self.stype.get()],
                yield_strength_MPa=g("Yield Strength (MPa)"),
                elastic_modulus_GPa=g("Elastic Modulus (GPa)"),
                force_N=g("Force / Axial Load (N)"),
                area_m2=g("Cross-section Area (m²)"),
                moment_Nm=g("Bending Moment (N·m)"),
                distance_m=g("Distance from NA (m)"),
                moment_of_inertia_m4=g("Moment of Inertia (m⁴)"),
                shear_force_N=g("Shear Force (N)"),
                torque_Nm=g("Torque (N·m)"),
                radius_m=g("Shaft Radius (m)"),
                polar_moment_m4=g("Polar Moment J (m⁴)"),
            )

            safety_label = (
                "✓ SAFE (FoS ≥ 1.5)" if res.safe
                else "✗ UNSAFE — FoS below 1.5"
            )
            safety_color = "SAFE" if res.safe else "DANGER"

            out = f"""{'─'*50}
  STRESS ANALYSIS RESULTS
{'─'*50}
  Stress type   : {self.stype.get()}
  Formula       : {res.formula_used}

  Calculated Stress   : {res.stress_MPa:.4f} MPa
  Yield Strength      : {self.entries['Yield Strength (MPa)'].get()} MPa
  Factor of Safety    : {res.factor_of_safety if res.factor_of_safety != float('inf') else '∞ (no load)'}
  Failure mode        : {res.failure_mode}
{'─'*50}
  {safety_label}
{'─'*50}"""

            if res.strain is not None:
                out += f"\n  Strain (ε)    : {res.strain:.6e}"
            if res.von_mises_MPa:
                out += f"\n  Von Mises σ   : {res.von_mises_MPa:.4f} MPa"

            write_result(self.out, out)
        except Exception as ex:
            messagebox.showerror("Calculation Error", str(ex))


# ── Tab 3: Moment of Inertia ───────────────────────────────────────────────────

class InertiaTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=PANEL)
        self._build()

    def _build(self):
        section_header(self, "⬡ Moment of Inertia — Section Properties")

        top = tk.Frame(self, bg=PANEL)
        top.pack(fill="x", padx=20, pady=8)

        styled_label(top, "Section type").grid(row=0, column=0, sticky="w", pady=3)
        self.section = tk.StringVar(value="Rectangle")
        self.combo = styled_combo(top, [
            "Rectangle", "Solid Circle", "Hollow Circle",
            "I-Section (H-Beam)", "T-Section", "Triangle"
        ], textvariable=self.section)
        self.combo.grid(row=0, column=1, sticky="w", padx=8)
        self.combo.bind("<<ComboboxSelected>>", self._update_fields)

        self.form = tk.Frame(self, bg=PANEL)
        self.form.pack(fill="x", padx=20, pady=4)
        self.entries = {}
        self._update_fields()

        tk.Button(self, text="▶  Calculate Section Properties",
                  font=("Segoe UI", 11, "bold"),
                  bg=BLUE, fg=DARK, relief="flat", padx=20, pady=8, cursor="hand2",
                  command=self._calculate).pack(pady=12)

        frame, self.out = result_box(self, height=14)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    def _clear_form(self):
        for w in self.form.winfo_children():
            w.destroy()
        self.entries = {}

    def _add_field(self, label, default, row):
        styled_label(self.form, label).grid(row=row, column=0, sticky="w", pady=3)
        v = tk.StringVar(value=default)
        e = styled_entry(self.form, textvariable=v)
        e.grid(row=row, column=1, sticky="w", padx=8)
        self.entries[label] = v

    def _update_fields(self, event=None):
        self._clear_form()
        s = self.section.get()
        defs = {
            "Rectangle": [("Width b (m)", "0.1"), ("Height h (m)", "0.2")],
            "Solid Circle": [("Diameter d (m)", "0.1")],
            "Hollow Circle": [("Outer Diameter D (m)", "0.12"), ("Inner Diameter d (m)", "0.1")],
            "I-Section (H-Beam)": [
                ("Flange width bf (m)", "0.15"), ("Flange thickness tf (m)", "0.012"),
                ("Web height hw (m)", "0.25"), ("Web thickness tw (m)", "0.008"),
            ],
            "T-Section": [
                ("Flange width bf (m)", "0.12"), ("Flange thickness tf (m)", "0.01"),
                ("Web height hw (m)", "0.20"), ("Web thickness tw (m)", "0.008"),
            ],
            "Triangle": [("Base b (m)", "0.1"), ("Height h (m)", "0.15")],
        }
        for i, (label, default) in enumerate(defs.get(s, [])):
            self._add_field(label, default, i)

    def _calculate(self):
        try:
            g = lambda k: float(self.entries[k].get())
            s = self.section.get()

            stype_map = {
                "Rectangle": (SectionType.RECTANGLE,
                    {"width_m": g("Width b (m)"), "height_m": g("Height h (m)")}),
                "Solid Circle": (SectionType.SOLID_CIRCLE,
                    {"diameter_m": g("Diameter d (m)")}),
                "Hollow Circle": (SectionType.HOLLOW_CIRCLE,
                    {"outer_diameter_m": g("Outer Diameter D (m)"), "inner_diameter_m": g("Inner Diameter d (m)")}),
                "I-Section (H-Beam)": (SectionType.I_SECTION, {
                    "flange_width_m": g("Flange width bf (m)"), "flange_thickness_m": g("Flange thickness tf (m)"),
                    "web_height_m": g("Web height hw (m)"), "web_thickness_m": g("Web thickness tw (m)"),
                }),
                "T-Section": (SectionType.T_SECTION, {
                    "flange_width_m": g("Flange width bf (m)"), "flange_thickness_m": g("Flange thickness tf (m)"),
                    "web_height_m": g("Web height hw (m)"), "web_thickness_m": g("Web thickness tw (m)"),
                }),
                "Triangle": (SectionType.TRIANGLE,
                    {"base_m": g("Base b (m)"), "height_m": g("Height h (m)")}),
            }
            stype, kwargs = stype_map[s]
            res = calculate_section(stype, **kwargs)

            out = f"""{'─'*50}
  SECTION PROPERTIES — {res.section_type.upper()}
{'─'*50}
  Cross-section Area    : {res.area_m2*1e6:.4f} mm²   ({res.area_m2:.6e} m²)
  Centroid (from base)  : {res.centroid_y_m*1000:.4f} mm

  ── Second Moment of Area ──
  Ixx (about x-x)       : {res.Ixx_m4:.6e} m⁴   ({res.Ixx_m4*1e8:.4f} × 10⁻⁸ m⁴)
  Iyy (about y-y)       : {res.Iyy_m4:.6e} m⁴
  J   (polar)           : {res.J_m4:.6e} m⁴

  ── Section Modulus ──
  Sx = Ixx/y_max        : {res.section_modulus_x_m3:.6e} m³
  Sy = Iyy/x_max        : {res.section_modulus_y_m3:.6e} m³

  ── Radius of Gyration ──
  rx = √(Ixx/A)         : {res.radius_gyration_x*1000:.4f} mm
  ry = √(Iyy/A)         : {res.radius_gyration_y*1000:.4f} mm
{'─'*50}"""
            write_result(self.out, out)
        except Exception as ex:
            messagebox.showerror("Calculation Error", str(ex))


# ── Tab 4: Unit Converter ──────────────────────────────────────────────────────

class UnitsTab(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=PANEL)
        self._build()

    def _build(self):
        section_header(self, "⬡ Engineering Unit Converter")

        form = tk.Frame(self, bg=PANEL)
        form.pack(fill="x", padx=20, pady=8)

        styled_label(form, "Category").grid(row=0, column=0, sticky="w", pady=3)
        cats = available_categories()
        self.category = tk.StringVar(value=cats[0])
        cat_combo = styled_combo(form, cats, textvariable=self.category)
        cat_combo.grid(row=0, column=1, sticky="w", padx=8)
        cat_combo.bind("<<ComboboxSelected>>", self._update_units)

        styled_label(form, "Value").grid(row=1, column=0, sticky="w", pady=3)
        self.value_var = tk.StringVar(value="1")
        styled_entry(form, textvariable=self.value_var).grid(row=1, column=1, sticky="w", padx=8)

        styled_label(form, "From unit").grid(row=2, column=0, sticky="w", pady=3)
        self.from_var = tk.StringVar()
        self.from_combo = styled_combo(form, [], textvariable=self.from_var)
        self.from_combo.grid(row=2, column=1, sticky="w", padx=8)

        styled_label(form, "To unit").grid(row=3, column=0, sticky="w", pady=3)
        self.to_var = tk.StringVar()
        self.to_combo = styled_combo(form, [], textvariable=self.to_var)
        self.to_combo.grid(row=3, column=1, sticky="w", padx=8)

        self._update_units()

        tk.Button(self, text="▶  Convert", font=("Segoe UI", 11, "bold"),
                  bg=BLUE, fg=DARK, relief="flat", padx=20, pady=8, cursor="hand2",
                  command=self._convert).pack(pady=12)

        frame, self.out = result_box(self, height=8)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

    def _update_units(self, event=None):
        units = list_units(self.category.get())
        self.from_combo["values"] = units
        self.to_combo["values"] = units
        self.from_var.set(units[0] if units else "")
        self.to_var.set(units[1] if len(units) > 1 else "")

    def _convert(self):
        try:
            val = float(self.value_var.get())
            res = convert(val, self.from_var.get(), self.to_var.get())

            out = f"""{'─'*50}
  UNIT CONVERSION
{'─'*50}
  Category      : {res.category.upper()}

  Input         : {res.from_value} {res.from_unit}
  Result        : {res.to_value} {res.to_unit}

  Conversion    : 1 {res.from_unit} = {res.conversion_factor} {res.to_unit}
{'─'*50}"""
            write_result(self.out, out)
        except Exception as ex:
            messagebox.showerror("Conversion Error", str(ex))


# ── Main Application ───────────────────────────────────────────────────────────

class EngineeringApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Engineering Calculator Toolkit")
        self.configure(bg=DARK)
        self.geometry("860x700")
        self.minsize(760, 580)
        self._build_header()
        self._build_tabs()
        self._build_status()

    def _build_header(self):
        h = tk.Frame(self, bg=PANEL, pady=12)
        h.pack(fill="x")
        tk.Label(h, text="⚙  ENGINEERING CALCULATOR TOOLKIT",
                 font=("Segoe UI", 14, "bold"), bg=PANEL, fg=BLUE).pack()
        tk.Label(h, text="Beam · Stress · Inertia · Units",
                 font=("Segoe UI", 9), bg=PANEL, fg=MUTED).pack()
        tk.Frame(self, bg=BLUE, height=2).pack(fill="x")

    def _build_tabs(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Eng.TNotebook", background=DARK, borderwidth=0)
        style.configure("Eng.TNotebook.Tab",
                        background=CARD, foreground=MUTED,
                        font=("Segoe UI", 10, "bold"),
                        padding=[16, 8], borderwidth=0)
        style.map("Eng.TNotebook.Tab",
                  background=[("selected", PANEL)],
                  foreground=[("selected", BLUE)])

        nb = ttk.Notebook(self, style="Eng.TNotebook")
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        tabs = [
            ("Beam Deflection", BeamTab),
            ("Stress & FoS", StressTab),
            ("Section Inertia", InertiaTab),
            ("Unit Converter", UnitsTab),
        ]
        for name, cls in tabs:
            frame = cls(nb)
            nb.add(frame, text=f"  {name}  ")

    def _build_status(self):
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x")
        status = tk.Frame(self, bg=DARK, pady=4)
        status.pack(fill="x")
        tk.Label(status, text=" Python Engineering Utility Tool v1.0  |  Beam · Stress · Inertia · Units",
                 font=("Segoe UI", 8), bg=DARK, fg=MUTED).pack(side="left")


def main():
    app = EngineeringApp()
    app.mainloop()


if __name__ == "__main__":
    main()
