"""
Engineering Toolkit — CLI launcher
Run: python main.py            → launches GUI
     python main.py --cli      → interactive CLI mode
     python main.py --test     → quick self-test
"""

import sys


def run_gui():
    from ui.app import main
    main()


def run_cli():
    """Minimal interactive CLI for quick calculations."""
    from core import (
        calculate_beam_deflection, BeamType, LoadType,
        calculate_stress, StressType,
        calculate_section, SectionType,
        convert,
    )

    print("\n╔══════════════════════════════════════╗")
    print("║  ENGINEERING CALCULATOR TOOLKIT CLI ║")
    print("╚══════════════════════════════════════╝\n")
    print("  1. Beam Deflection")
    print("  2. Stress & Factor of Safety")
    print("  3. Section Moment of Inertia")
    print("  4. Unit Conversion")
    print("  0. Exit\n")

    choice = input("Select module: ").strip()

    if choice == "1":
        print("\n── Beam Deflection ──")
        L = float(input("Beam length (m): "))
        P = float(input("Total load (N): "))
        E = float(input("Elastic modulus (GPa) [steel=200]: ") or "200")
        I = float(input("Moment of inertia (m⁴): "))
        bt = input("Beam type [ss/c/ff]: ").strip().lower()
        lt = input("Load type [p/u]: ").strip().lower()

        bt_map = {"ss": BeamType.SIMPLY_SUPPORTED, "c": BeamType.CANTILEVER, "ff": BeamType.FIXED_FIXED}
        lt_map = {"p": LoadType.POINT_LOAD, "u": LoadType.UDL}

        res = calculate_beam_deflection(
            bt_map.get(bt, BeamType.SIMPLY_SUPPORTED),
            lt_map.get(lt, LoadType.POINT_LOAD),
            L, P, E, I,
        )
        print(f"\nMax Deflection     : {res.max_deflection_mm:.4f} mm")
        print(f"Max Bending Moment : {res.max_bending_moment_Nm:,.2f} N·m")
        print(f"Max Shear Force    : {res.max_shear_force_N:,.2f} N")
        print(f"Formula            : {res.formula_used}")
        if res.warning:
            print(f"⚠  {res.warning}")

    elif choice == "2":
        print("\n── Stress Calculator ──")
        F = float(input("Force (N): "))
        A = float(input("Area (m²): "))
        Sy = float(input("Yield strength (MPa): "))
        res = calculate_stress(StressType.NORMAL, Sy, force_N=F, area_m2=A)
        print(f"\nStress    : {res.stress_MPa:.4f} MPa")
        print(f"FoS       : {res.factor_of_safety}")
        print(f"Status    : {'✓ SAFE' if res.safe else '✗ UNSAFE'}")

    elif choice == "3":
        print("\n── Rectangle Moment of Inertia ──")
        b = float(input("Width b (m): "))
        h = float(input("Height h (m): "))
        from core.inertia import rectangle
        res = rectangle(b, h)
        print(f"\nArea  : {res.area_m2*1e6:.2f} mm²")
        print(f"Ixx   : {res.Ixx_m4:.6e} m⁴")
        print(f"Iyy   : {res.Iyy_m4:.6e} m⁴")

    elif choice == "4":
        print("\n── Unit Converter ──")
        v = float(input("Value: "))
        f = input("From unit: ")
        t = input("To unit  : ")
        res = convert(v, f, t)
        print(f"\n  {res.from_value} {res.from_unit} = {res.to_value} {res.to_unit}")

    elif choice == "0":
        sys.exit(0)


def run_tests():
    import subprocess
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        cwd=__file__.replace("main.py", ""),
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--cli" in args:
        run_cli()
    elif "--test" in args:
        run_tests()
    else:
        run_gui()
