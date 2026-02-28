"""
Mesh Analysis Solver
====================
Solves electrical circuit mesh analysis problems using KVL
(Kirchhoff's Voltage Law).

Supports:
    - Resistors, voltage sources, and current sources
    - Common (shared) resistors between meshes
    - Up to 9 meshes with automatic direction detection

Usage:
    python MESHSUBMIT.py
    Follow the interactive prompts to enter circuit data.
"""

from sympy import Eq, solve
import sympy as sp


# ─── Constants ────────────────────────────────────────────────────────────────
OHM_SYMBOL = chr(937)  # Ω

# ─── ANSI Color Codes ────────────────────────────────────────────────────────
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[1;36m"
WHITE = "\033[1;37m"
RESET = "\033[0m"

# ─── Global Counters ─────────────────────────────────────────────────────────
total_resistor_count = 0
total_voltage_count = 0
total_current_source_count = 0
common_resistor_pair_count = 0

# ─── Global Data Stores ──────────────────────────────────────────────────────
resistor_keys = []
resistor_values_list = []
voltage_keys = []
voltage_values_list = []

mesh_elements = {}    # {"Mesh1": {"R1": "5", "V1": "-10", "CR2": -3.0}, ...}
current_sources = {}  # {"i1": 5.0, "i2": -3.0, ...}


# ═══════════════════════════════════════════════════════════════════════════════
#                          INPUT COLLECTION
# ═══════════════════════════════════════════════════════════════════════════════

def collect_resistors(mesh_number: int) -> dict:
    """
    Prompt the user for resistor values and an optional current source for a mesh.

    Updates global mesh_elements, current_sources, and resistor tracking lists.

    Args:
        mesh_number: 1-indexed mesh identifier.

    Returns:
        Mapping of all collected resistor labels to their float values.
    """
    global total_current_source_count, total_resistor_count

    if total_current_sources_in_circuit != 0:
        current_value = float(input(
            f"Enter the value of current source in Mesh {mesh_number} (in C.W) : "
        ))
        if current_value != 0:
            total_current_source_count = (
                1 if mesh_number == 1 else total_current_source_count + 1
            )
            current_sources[f"i{mesh_number}"] = current_value
        else:
            total_current_source_count = 1
    else:
        total_current_source_count = 1

    raw_values = input("Enter the values of all resistors(Ex: 2,5,10) : ").split(",")

    total_resistor_count = (
        len(raw_values) if mesh_number == 1
        else total_resistor_count + len(raw_values)
    )

    for idx, raw_val in enumerate(raw_values, start=1):
        value = float(raw_val)
        mesh_label = f"Mesh{mesh_number}-R{idx}"

        print(f"{mesh_label} = {raw_val} {OHM_SYMBOL}")

        resistor_keys.append(mesh_label)
        resistor_values_list.append(value)
        mesh_elements.setdefault(f"Mesh{mesh_number}", {})[f"R{idx}"] = raw_val

    print()
    return dict(zip(resistor_keys, resistor_values_list))


def collect_voltages(mesh_number: int) -> dict:
    """
    Prompt the user for voltage source values for a mesh.

    Updates global mesh_elements and voltage tracking lists.

    Args:
        mesh_number: 1-indexed mesh identifier.

    Returns:
        Mapping of all collected voltage labels to their float values.
    """
    global total_voltage_count

    raw_values = input(
        "Enter the values of all voltage sources(in C.W)[Ex: -5,10,20] : "
    ).split(",")

    total_voltage_count = (
        len(raw_values) if mesh_number == 1
        else total_voltage_count + len(raw_values)
    )

    if raw_values:
        for idx, raw_val in enumerate(raw_values, start=1):
            value = float(raw_val)
            mesh_label = f"Mesh{mesh_number}-V{idx}"

            print(f"{mesh_label} = {raw_val} V")

            voltage_keys.append(mesh_label)
            voltage_values_list.append(value)
            mesh_elements.setdefault(f"Mesh{mesh_number}", {})[f"V{idx}"] = raw_val

        print()
        return dict(zip(voltage_keys, voltage_values_list))

    return {}


def collect_common_resistors(num_meshes: int) -> list:
    """
    Prompt the user for common resistor values shared between mesh pairs.

    Updates global mesh_elements with negative common resistance entries
    (representing coupling between meshes in KVL).

    Args:
        num_meshes: Total number of meshes in the circuit.

    Returns:
        List of common resistor values (as floats).
    """
    global common_resistor_pair_count

    if num_meshes <= 1:
        return []

    num_common = int(input("Enter the no.of Common resistors B/W Meshes : "))
    common_resistor_pair_count = num_common
    collected = 0
    common_values = []

    print("\nEnter Common resistance values B/W meshes : ")

    while collected < num_common:
        if num_common != 1:
            for i in range(1, num_meshes + 1):
                for j in range(i + 1, num_meshes + 1):
                    collected += 1
                    value = float(input(f"Mesh {i} and Mesh {j} = "))
                    print()
                    common_values.append(value)
                    mesh_elements.setdefault(f"Mesh{i}", {})[f"CR{j}"] = -value
                    mesh_elements.setdefault(f"Mesh{j}", {})[f"CR{i}"] = -value
        else:
            collected += 1
            value = float(input("Mesh 1 and Mesh 2 = "))
            common_values.append(value)
            mesh_elements.setdefault("Mesh1", {})["CR2"] = -value
            mesh_elements.setdefault("Mesh2", {})["CR1"] = -value

        print()

    return common_values


# ═══════════════════════════════════════════════════════════════════════════════
#                       EQUATION BUILDING & SOLVING
# ═══════════════════════════════════════════════════════════════════════════════

def build_kvl_equation_terms() -> list:
    """
    Build KVL equation terms for each mesh from collected mesh_elements.

    Each mesh's terms include:
        - Resistor contributions  (R * I_mesh)
        - Voltage source values
        - Common resistor coupling terms (CR * I_adjacent)

    Returns:
        Nested list where each inner list contains string terms
        for one mesh's KVL equation.
    """
    equation_terms = []
    search_limit = (
        total_resistor_count * total_voltage_count * total_current_source_count
    ) + 10

    for mesh_key, elements in mesh_elements.items():
        mesh_num = mesh_key[4]
        terms = []

        for element_key in elements:
            for i in range(1, search_limit + 1):
                if element_key == f"R{i}":
                    resistance = elements[f"R{i}"]
                    terms.append(f"{resistance}*i{mesh_num}")
                elif element_key == f"V{i}":
                    voltage = elements[f"V{i}"]
                    terms.append(voltage)
                elif element_key == f"CR{i}":
                    common_coeff = elements[f"CR{i}"]
                    terms.append(f"{common_coeff}*i{i}")

        equation_terms.append(terms)

    return equation_terms


def solve_mesh_equations(equation_terms: list, num_meshes: int) -> dict:
    """
    Convert KVL equation terms to symbolic equations and solve for mesh currents.

    Args:
        equation_terms: Nested list of string terms for each mesh equation.
        num_meshes:     Total number of meshes.

    Returns:
        Dictionary of solved mesh current values, sorted by mesh index.
    """
    mesh_symbols = [sp.symbols(f"i{x}") for x in range(1, num_meshes + 1)]
    equations = []

    for terms in equation_terms:
        mesh_sum = 0
        for term in terms:
            for i in range(1, num_meshes + 1):
                term = term.replace(f"i{i}", str(mesh_symbols[i - 1]))
            mesh_sum += sp.simplify(term)
        equations.append(mesh_sum)

    # Build system of equations (KVL = 0, or constrained by current sources)
    equation_system = {}
    for i in range(1, len(equation_terms) + 1):
        if f"i{i}" not in current_sources:
            equation_system[f"eq{i}"] = Eq(equations[i - 1], 0)
        else:
            equation_system[f"eq{i}"] = Eq(
                sp.simplify(f"i{i}"), -current_sources[f"i{i}"]
            )

    solution = solve(equation_system.values())

    # Convert solution to mesh current values
    mesh_current_values = {}
    source_labels = list(current_sources.keys())

    if source_labels:
        for symbol, value in solution.items():
            for label in source_labels:
                if str(symbol) not in source_labels:
                    mesh_current_values[str(symbol)] = -1 * value
                else:
                    mesh_current_values[label] = current_sources[label]
    else:
        for symbol, value in solution.items():
            mesh_current_values[str(symbol)] = -1 * value

    # Sort mesh currents in order: i1, i2, i3, ...
    sorted_currents = {}
    for i in range(1, num_meshes + 1):
        sorted_currents[f"i{i}"] = mesh_current_values[f"i{i}"]

    return sorted_currents


# ═══════════════════════════════════════════════════════════════════════════════
#                     COMMON RESISTOR CURRENT COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════════

def compute_common_resistor_currents(mesh_current_values: dict) -> dict:
    """
    Calculate the current through each common resistor using mesh current
    differences.

    Args:
        mesh_current_values: Solved mesh currents.

    Returns:
        Dictionary mapping common resistor labels to their current values.
    """
    common_currents = {}

    for mesh_key, elements in mesh_elements.items():
        for element_key, element_value in elements.items():
            if "CR" in element_key and int(element_value) != 0:
                first_mesh = int(mesh_key[4:])
                second_mesh = int(element_key[2:])
                resistance = -1 * int(element_value)
                label = f"I-R{first_mesh}{second_mesh}({resistance}{OHM_SYMBOL})"

                current_diff = round(
                    round(float(mesh_current_values[f"i{first_mesh}"]), 4)
                    - round(float(mesh_current_values[f"i{second_mesh}"]), 4),
                    2,
                )
                common_currents[label] = current_diff

    return common_currents


def remove_duplicate_pairs(common_currents: dict, num_meshes: int) -> dict:
    """
    Remove duplicate common resistor pair entries (e.g., keep I-R12 but
    remove I-R21) since they represent the same branch.

    Args:
        common_currents: Dictionary of common resistor currents.
        num_meshes:      Total number of meshes.

    Returns:
        Filtered dictionary with duplicate pairs removed.
    """
    all_pairs = []

    if common_resistor_pair_count == 1:
        upper_bound = 3  # Only two meshes share a resistor
    else:
        upper_bound = common_resistor_pair_count + num_meshes

    for i in range(1, upper_bound):
        for j in range(1, upper_bound):
            if i != j:
                all_pairs.append(f"{i}{j}")

    # Identify reversed duplicates (e.g., "21" is the reverse of "12")
    duplicates_to_remove = []
    for pair in all_pairs:
        reversed_pair = pair[::-1]
        if reversed_pair in all_pairs:
            duplicates_to_remove.append(
                all_pairs.pop(all_pairs.index(reversed_pair))
            )

    # Remove duplicate entries from common_currents
    filtered = dict(common_currents)
    for dup_pair in duplicates_to_remove:
        for key in list(filtered.keys()):
            if dup_pair in key:
                del filtered[key]

    return filtered


# ═══════════════════════════════════════════════════════════════════════════════
#                            DISPLAY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def display_instructions():
    """Print formatted usage instructions to the console."""
    print(f"                 {GREEN}!! INSTRUCTIONS !!{RESET}                   ")
    print(
        f"{YELLOW}(1){RESET} {CYAN}Enter resistance and voltage values by using (comma)\n"
        f"Example : 2,3,4{RESET}\n"
    )
    print(
        f"{YELLOW}(2){RESET} {CYAN}For voltage and current sources Enter with sign\n"
        f"CW - clock wise direction(+ve)\n"
        f"A.CW - anticlock wise direction(-ve)-->(Ex : 5,-10){RESET}\n"
    )
    print(
        f"{YELLOW}(3){RESET} {CYAN}Units should be in :\n"
        f"Resistance -- ohms({OHM_SYMBOL})(Ex : 2,3,5)\n"
        f"Voltage values -- volts(V) (Ex : -5,10,20)\n"
        f"Current source -- Amperes(A) (Ex : 5,-10){RESET}\n"
    )
    print(
        f"{YELLOW}(4){RESET} {CYAN}Assume all mesh currents are in (C.W) "
        f"direction{RESET}\n\n"
    )
    print(
        f"{YELLOW}(5){RESET} {CYAN}NOTE: Include common resistors inside "
        f"mesh resistor lists{RESET}\n\n"
    )


def display_mesh_currents(mesh_current_values: dict):
    """
    Print solved mesh currents with direction indicators (CW or ACW).

    Args:
        mesh_current_values: Solved mesh current values.
    """
    print(f"{YELLOW} Mesh Currents : {RESET}")

    for label, value in mesh_current_values.items():
        current = float(value)
        mesh_num = label[1:]

        if current < 0:
            print(
                f"{WHITE}Mesh {mesh_num}  -->  {label} = "
                f"{round(-current, 2)} A in (A.CW){RESET} "
            )
        elif current > 0:
            print(
                f"{WHITE}Mesh {mesh_num}  -->  {label} = "
                f"{round(current, 2)} A in (CW) "
            )
        else:
            print(
                f"{WHITE}Mesh {mesh_num}  -->  {label} = "
                f"{round(current, 2)} A "
            )


def display_common_resistor_currents(
    common_currents: dict, mesh_current_values: dict
):
    """
    Print current through common resistors with flow direction.

    The direction is determined by comparing the absolute magnitudes of
    the two mesh currents sharing the resistor.

    Args:
        common_currents:     Dictionary of common resistor currents.
        mesh_current_values: Solved mesh current values.
    """
    print(f"\n{YELLOW}Current through common resistors : {RESET}")

    for label, current in common_currents.items():
        mesh_i = label[3]
        mesh_j = label[4]

        abs_current_i = abs(float(mesh_current_values[f"i{mesh_i}"]))
        abs_current_j = abs(float(mesh_current_values[f"i{mesh_j}"]))
        display_value = abs(current)

        if abs_current_i < abs_current_j:
            print(
                f"{WHITE}{label} = {display_value} A "
                f"(in the direction of i{mesh_j}){RESET}"
            )
        elif abs_current_i > abs_current_j:
            print(
                f"{WHITE}{label} = {display_value} A "
                f"(in the direction of i{mesh_i}){RESET}"
            )
        elif current == 0:
            print(f"{WHITE}{label} = 0 A{RESET}")


# ═══════════════════════════════════════════════════════════════════════════════
#                              MAIN PROGRAM
# ═══════════════════════════════════════════════════════════════════════════════

display_instructions()

print(f"{YELLOW}                  MESH ANALYSIS                       {RESET}\n")

num_meshes = int(input("Enter no of Meshes : "))
total_current_sources_in_circuit = int(input(
    "Enter the total no of Current sources in the circuit "
    "(if no current source enter 0(zero)) : "
))

# ─── Step 1: Collect Circuit Data ─────────────────────────────────────────────
resistance_mapping = {}
voltage_mapping = {}

for i in range(1, num_meshes + 1):
    print(f"Mesh {i}")
    resistance_mapping.update(collect_resistors(i))

for i in range(1, num_meshes + 1):
    print(f"Mesh {i}")
    voltage_mapping.update(collect_voltages(i))

common_resistor_values = []
if num_meshes > 1:
    common_resistor_values.extend(collect_common_resistors(num_meshes))

# ─── Step 2: Build and Solve KVL Equations ────────────────────────────────────
equation_terms = build_kvl_equation_terms()
mesh_current_values = solve_mesh_equations(equation_terms, num_meshes)

# ─── Step 3: Compute Common Resistor Currents ────────────────────────────────
common_resistor_currents = compute_common_resistor_currents(mesh_current_values)

if num_meshes > 1 and common_resistor_pair_count != 0:
    common_resistor_currents = remove_duplicate_pairs(
        common_resistor_currents, num_meshes
    )

# ─── Step 4: Display Results ─────────────────────────────────────────────────
display_mesh_currents(mesh_current_values)

if num_meshes > 1 and num_meshes <= 9 and common_resistor_pair_count != 0:
    display_common_resistor_currents(common_resistor_currents, mesh_current_values)








