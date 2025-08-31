from sympy import Eq, solve
import sympy as sp
from colorama import init, Fore, Style

init(autoreset=True)

# ===========================================
# Mesh Analysis Program
# ===========================================
# Performs mesh analysis for electrical circuits.
# Features:
# - Handles multiple meshes
# - Supports resistors, voltage sources, and current sources
# - Handles common resistors
# - Computes mesh currents
# ===========================================

# ---------- GLOBAL VARIABLES ----------
TME1 = {}
currents_dict = {}
mesh_equations_list = []
mesh_currents = {}
common_resistor_count = 0


def input_resistors(mesh_no):
    """Collect resistor values for a given mesh."""
    if total_current_sources != 0:
        current_source_val = float(input(f"Enter the value of current source in Mesh {mesh_no} (in C.W) : "))
        if current_source_val != 0:
            currents_dict[f"i{mesh_no}"] = current_source_val

    resistor_values = list(input("Enter resistor values (Ex: 2,5,10): ").split(','))
    global total_resistors
    total_resistors += len(resistor_values)

    for idx, resistor in enumerate(resistor_values, start=1):
        print(f"Mesh {mesh_no} - R{idx} = {resistor} Ohm")
        TME1.setdefault(f"Mesh{mesh_no}", {})[f"R{idx}"] = resistor
    print()


def input_voltages(mesh_no):
    """Collect voltage source values for a given mesh."""
    voltage_values = list(input("Enter voltage source values (Ex: -5,10,20): ").split(','))
    global total_voltages
    total_voltages += len(voltage_values)

    for idx, voltage in enumerate(voltage_values, start=1):
        print(f"Mesh {mesh_no} - V{idx} = {voltage} V")
        TME1.setdefault(f"Mesh{mesh_no}", {})[f"V{idx}"] = voltage
    print()


def input_common_resistors(mesh_no):
    """Collect common resistor values between meshes."""
    if mesh_no > 1:
        n = int(input("Enter number of common resistors between meshes: "))
        global common_resistor_count
        common_resistor_count = n

        print("\nEnter common resistance values between meshes:")
        for i in range(1, mesh_no):
            for j in range(i + 1, mesh_no + 1):
                cr_value = float(input(f"Mesh {i} and Mesh {j} = "))
                TME1.setdefault(f"Mesh{i}", {})[f"CR{j}"] = -cr_value
                TME1.setdefault(f"Mesh{j}", {})[f"CR{i}"] = -cr_value
        print()


def build_kvl_equations(num_meshes):
    """Builds KVL equations for all meshes."""
    for mesh_name in TME1:
        mesh_idx = mesh_name[4]
        temp_list = []
        for key in TME1[mesh_name]:
            if key.startswith("R"):
                temp_list.append(f"{TME1[mesh_name][key]}*i{mesh_idx}")
            elif key.startswith("V"):
                temp_list.append(TME1[mesh_name][key])
            elif key.startswith("CR"):
                other_idx = key[2:]
                temp_list.append(f"{TME1[mesh_name][key]}*i{other_idx}")
        mesh_equations_list.append(temp_list)


def solve_mesh_currents(num_meshes):
    """Solves for mesh currents using SymPy."""
    symbols_list = [sp.symbols(f"i{x}") for x in range(1, num_meshes + 1)]
    equations = []

    for mesh_terms in mesh_equations_list:
        mesh_sum = 0
        for term in mesh_terms:
            for i in range(1, num_meshes + 1):
                term = term.replace(f"i{i}", str(symbols_list[i - 1]))
            mesh_sum += sp.simplify(term)
        equations.append(mesh_sum)

    equation_dict = {}
    for i in range(1, len(mesh_equations_list) + 1):
        if f"i{i}" not in currents_dict.keys():
            equation_dict[f"eq{i}"] = Eq(equations[i - 1], 0)
        else:
            equation_dict[f"eq{i}"] = Eq(sp.simplify(f"i{i}"), -currents_dict[f"i{i}"])

    solution = solve(equation_dict.values())
    return {f"i{i}": (-1 * solution[symbols_list[i - 1]]) for i in range(1, num_meshes + 1)}


def main():
    print(Fore.GREEN + "!! INSTRUCTIONS !!" + Style.RESET_ALL)
    print(Fore.YELLOW + "(1)" + Fore.CYAN + " Enter resistance and voltage values separated by commas (Ex: 2,3,4)")
    print(Fore.YELLOW + "(2)" + Fore.CYAN + " For voltage/current sources, enter with sign (+ CW, - ACW)")
    print(Fore.YELLOW + "(3)" + Fore.CYAN + " Units: Resistance in Ohm, Voltage in V, Current in A")
    print(Fore.YELLOW + "(4)" + Fore.CYAN + " Assume all mesh currents are in CW direction\n")
    print(Fore.YELLOW + "MESH ANALYSIS\n" + Style.RESET_ALL)

    num_meshes = int(input("Enter number of meshes: "))
    global total_current_sources, total_resistors, total_voltages
    total_current_sources = int(input("Enter total number of current sources (0 if none): "))
    total_resistors, total_voltages = 0, 0

    for i in range(1, num_meshes + 1):
        print(f"Mesh {i}")
        input_resistors(i)

    for i in range(1, num_meshes + 1):
        print(f"Mesh {i}")
        input_voltages(i)

    if num_meshes > 1:
        input_common_resistors(num_meshes)

    build_kvl_equations(num_meshes)
    global mesh_currents
    mesh_currents = solve_mesh_currents(num_meshes)

    print(Fore.YELLOW + "Mesh Currents:\n" + Style.RESET_ALL)
    for key, value in mesh_currents.items():
        current = float(value)
        direction = "(CW)" if current > 0 else "(A.CW)" if current < 0 else ""
        print(f"Mesh {key[1:]} --> {key} = {abs(round(current, 2))} A {direction}")


if __name__ == "__main__":
    main()
