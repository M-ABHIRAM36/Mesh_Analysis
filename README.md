# Mesh Analysis Solver (Python)

A general-purpose **mesh analysis solver** for planar electrical circuits. It computes mesh currents by automatically constructing and solving Kirchhoff's Voltage Law (KVL) equations using symbolic algebra.

Originally developed during **B.Tech 1st Year** as a foundational circuits project, then **refactored and improved in 3rd Year** with clean architecture, proper naming conventions, docstrings, and modular function design.

---

## Table of Contents

1. [Features](#features)
2. [How Mesh Analysis Works](#how-mesh-analysis-works)
3. [Algorithm Overview](#algorithm-overview)
4. [Requirements](#requirements)
5. [Installation](#installation)
6. [How to Run](#how-to-run)
7. [Input Instructions](#input-instructions)
8. [Examples](#examples)
   - [Example 1 -- Single Mesh](#example-1--single-mesh-1-mesh)
   - [Example 2 -- Two Meshes with Shared Resistor](#example-2--two-meshes-with-shared-resistor)
   - [Example 3 -- Three Meshes](#example-3--three-meshes-with-two-shared-resistors)
   - [Example 4 -- Two Meshes with Multiple Voltage Sources](#example-4--two-meshes-with-multiple-voltage-sources)
   - [Example 5 -- Two Meshes with a Current Source](#example-5--two-meshes-with-a-current-source)
9. [Project Structure](#project-structure)
10. [Future Improvements](#future-improvements)
11. [Author](#author)
12. [License](#license)

---

## Features

| Capability | Description |
|---|---|
| **Unlimited meshes** | Supports any number of meshes (practical limit: 9 for common-resistor labelling) |
| **Shared resistors** | Handles common resistors between any pair of meshes |
| **Voltage sources** | Supports multiple voltage sources per mesh with sign convention |
| **Current sources** | Supports current source constraints on individual meshes |
| **Automatic KVL equations** | Equation terms are generated programmatically from user input |
| **Symbolic solving** | Uses SymPy's symbolic engine -- exact rational/algebraic solutions |
| **Direction detection** | Reports whether each mesh current flows Clockwise (CW) or Anti-Clockwise (A.CW) |
| **Common resistor currents** | Calculates and displays current through every shared branch with flow direction |

---

## How Mesh Analysis Works

Mesh analysis is a systematic method for solving planar circuits. It is based on two principles:

1. **Kirchhoff's Voltage Law (KVL):** The algebraic sum of all voltages around any closed loop (mesh) is zero.
2. **Mesh currents:** A fictitious current variable is assigned to each mesh, assumed to flow in the **clockwise** direction by convention.

### Procedure

1. Assign a mesh current ($i_1, i_2, \ldots, i_n$) to each independent loop.
2. For each mesh, write a KVL equation:
   - Resistors exclusive to the mesh contribute $R \cdot i_k$.
   - Shared (common) resistors contribute a coupling term $R_c \cdot (i_k - i_j)$ between adjacent meshes $k$ and $j$.
   - Voltage sources add or subtract their value depending on polarity relative to the assumed current direction.
3. If a mesh contains a **current source**, the mesh current on that loop is directly constrained by the source value instead of a KVL equation.
4. Solve the resulting system of $n$ linear equations for $n$ unknowns.

A **negative** solution for a mesh current indicates the actual current flows **anti-clockwise** (opposite to the assumed direction).

---

## Algorithm Overview

```
START
  |
  v
[1] Read number of meshes (n) and number of current sources
  |
  v
[2] For each mesh:
      - Collect resistor values --> store in mesh_elements
      - If current source exists, record constraint
  |
  v
[3] For each mesh:
      - Collect voltage source values --> store in mesh_elements
  |
  v
[4] If n > 1:
      - Collect common (shared) resistor values between mesh pairs
      - Store negative coupling coefficients in mesh_elements
  |
  v
[5] Build KVL equation terms for each mesh:
      - Self-resistance terms:    R * i_k
      - Voltage terms:            V  (constant)
      - Coupling terms:          -R_common * i_adjacent
  |
  v
[6] Convert string terms to SymPy symbolic expressions
  |
  v
[7] Construct equation system:
      - Standard mesh:   sum_of_terms = 0   (KVL)
      - Current source:  i_k = I_source     (constraint)
  |
  v
[8] Solve using sympy.solve()
  |
  v
[9] Compute current through each common resistor:
      I_branch = i_k - i_j
  |
  v
[10] Remove duplicate branch pairs (R12 == R21)
  |
  v
[11] Display results with direction indicators
  |
END
```

---

## Requirements

| Dependency | Version | Purpose |
|---|---|---|
| **Python** | 3.8+ | Runtime |
| **SymPy** | >= 1.12 | Symbolic equation construction and linear system solving |

### Optional

| Package | Purpose |
|---|---|
| **colorama** | Enables ANSI color support on older Windows terminals (CMD on Windows 8/7). Not needed on Windows 10+, Windows Terminal, PowerShell 7, or Linux/macOS. |

The solver uses raw ANSI escape codes for colored terminal output. These work natively on all modern terminals. Install `colorama` only if you see garbled output on a legacy Windows console.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/mesh_analysis.git
cd mesh_analysis
```

### 2. (Recommended) Create a virtual environment

```bash
python -m venv venv
```

Activate it:

| OS | Command |
|---|---|
| Windows (PowerShell) | `.\venv\Scripts\Activate.ps1` |
| Windows (CMD) | `.\venv\Scripts\activate.bat` |
| Linux / macOS | `source venv/bin/activate` |

### 3. Install dependencies

Using the requirements file:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install sympy
```

To verify installation:

```bash
python -c "import sympy; print(sympy.__version__)"
```

---

## How to Run

```bash
python Mesh_solver.py
```

The program launches an interactive terminal session. Follow the on-screen prompts to enter your circuit data. Results are displayed immediately after solving.

---

## Input Instructions

| Parameter | Format | Notes |
|---|---|---|
| **Number of meshes** | Integer (e.g., `2`) | Total independent loops in the circuit |
| **Current sources** | Integer count, then value per mesh | Enter `0` if mesh has no current source. Positive = CW, Negative = A.CW |
| **Resistor values** | Comma-separated (e.g., `2,5,10`) | Enter all resistors in the mesh, **including** any shared resistor |
| **Voltage sources** | Comma-separated with sign (e.g., `-5,10`) | Positive = voltage rise in CW direction, Negative = voltage drop |
| **Common resistors** | One value per mesh pair | The shared resistance between Mesh i and Mesh j |

### Sign Convention

All values follow the **clockwise (CW) positive** convention:

- A voltage source whose positive terminal is encountered first when traversing the mesh clockwise is **positive**.
- A voltage source whose negative terminal is encountered first is **negative**.
- A current source flowing in the CW direction of the mesh is **positive**; A.CW is **negative**.

### Important Notes

- Common resistors must also be included in each mesh's individual resistor list.
- Enter `0` for current source value if the mesh does not contain one.
- Units: Resistance in Ohms, Voltage in Volts, Current in Amperes.

---

## Examples

### Example 1 -- Single Mesh (1 Mesh)

**Circuit:** A single loop with a 10V voltage source and two resistors (2 Ohm, 3 Ohm) in series.

```
        +---[ 2 Ohm ]---[ 3 Ohm ]---+
        |                            |
      (+)                            |
       10V                           |
      (-)                            |
        |                            |
        +----------------------------+
                  Mesh 1 (i1 -->)
```

**Input:**

```
Enter no of Meshes : 1
Enter the total no of Current sources in the circuit (if no current source enter 0(zero)) : 0
Mesh 1
Enter the values of all resistors(Ex: 2,5,10) : 2,3
Mesh1-R1 = 2 Ohm
Mesh1-R2 = 3 Ohm

Mesh 1
Enter the values of all voltage sources(in C.W)[Ex: -5,10,20] : 10
Mesh1-V1 = 10 V
```

**Output:**

```
 Mesh Currents :
Mesh 1  -->  i1 = 2.0 A in (CW)
```

**Verification:** $i_1 = \frac{10}{2 + 3} = 2.0\ \text{A}$

---

### Example 2 -- Two Meshes with Shared Resistor

**Circuit:** Two meshes sharing a 3 Ohm resistor. Mesh 1 has a 10V source and resistors 2 Ohm, 3 Ohm. Mesh 2 has a 5V source and resistors 3 Ohm, 4 Ohm.

```
        +--[ 2 Ohm ]--+--[ 4 Ohm ]--+
        |              |              |
      (+)          [ 3 Ohm ]        (+)
       10V         (shared)          5V
      (-)              |            (-)
        |              |              |
        +--------------+--------------+
          Mesh 1 (i1)    Mesh 2 (i2)
```

**Input:**

```
Enter no of Meshes : 2
Enter the total no of Current sources in the circuit (if no current source enter 0(zero)) : 0
Mesh 1
Enter the values of all resistors(Ex: 2,5,10) : 2,3
Mesh 2
Enter the values of all resistors(Ex: 2,5,10) : 3,4
Mesh 1
Enter the values of all voltage sources(in C.W)[Ex: -5,10,20] : 10
Mesh 2
Enter the values of all voltage sources(in C.W)[Ex: -5,10,20] : 5
Enter the no.of Common resistors B/W Meshes : 1

Enter Common resistance values B/W meshes :
Mesh 1 and Mesh 2 = 3
```

**Output:**

```
 Mesh Currents :
Mesh 1  -->  i1 = 2.83 A in (CW)
Mesh 2  -->  i2 = 1.93 A in (CW)

Current through common resistors :
I-R12(3 Ohm) = 0.9 A (in the direction of i1)
```

**Verification (KVL):**

Mesh 1: $5 i_1 - 3 i_2 = 10$

Mesh 2: $-3 i_1 + 7 i_2 = 5$

Solving: $i_1 \approx 2.83\ \text{A},\quad i_2 \approx 1.93\ \text{A}$

Current through shared resistor: $i_1 - i_2 = 0.90\ \text{A}$ (direction of $i_1$).

---

### Example 3 -- Three Meshes with Two Shared Resistors

**Circuit:** Three meshes. Mesh 1 and Mesh 2 share a 4 Ohm resistor. Mesh 2 and Mesh 3 share a 6 Ohm resistor. Each mesh has its own voltage source.

```
    +--[3 Ohm]--+--[5 Ohm]--+--[2 Ohm]--+
    |            |            |            |
  (+)        [4 Ohm]      [6 Ohm]       (+)
   20V       shared       shared         10V
  (-)            |            |          (-)
    |            |            |            |
    +------------+--[8 Ohm]--+------------+
      Mesh 1        Mesh 2       Mesh 3
```

**Input:**

```
Enter no of Meshes : 3
Enter the total no of Current sources in the circuit (if no current source enter 0(zero)) : 0
Mesh 1
Enter the values of all resistors(Ex: 2,5,10) : 3,4
Mesh 2
Enter the values of all resistors(Ex: 2,5,10) : 4,5,6,8
Mesh 3
Enter the values of all resistors(Ex: 2,5,10) : 6,2
Mesh 1
Enter the values of all voltage sources(in C.W)[Ex: -5,10,20] : 20
Mesh 2
Enter the values of all voltage sources(in C.W)[Ex: -5,10,20] : -15
Mesh 3
Enter the values of all voltage sources(in C.W)[Ex: -5,10,20] : 10
Enter the no.of Common resistors B/W Meshes : 2

Enter Common resistance values B/W meshes :
Mesh 1 and Mesh 2 = 4
Mesh 1 and Mesh 3 = 0
Mesh 2 and Mesh 3 = 6
```

**Output:**

```
 Mesh Currents :
Mesh 1  -->  i1 = 2.82 A in (CW)
Mesh 2  -->  i2 = 0.07 A in (A.CW)
Mesh 3  -->  i3 = 1.30 A in (CW)

Current through common resistors :
I-R12(4 Ohm) = 2.89 A (in the direction of i1)
I-R23(6 Ohm) = 1.37 A (in the direction of i3)
```

**Note:** Enter `0` for the common resistance between Mesh 1 and Mesh 3 since they do not share a resistor.

---

### Example 4 -- Two Meshes with Multiple Voltage Sources

**Circuit:** Two meshes with multiple voltage sources per mesh. Mesh 1 has two voltage sources (20V and -5V). Mesh 2 has one voltage source (10V). The meshes share a 5 Ohm resistor.

```
    +--[3 Ohm]---(+20V-)---+---(-5V+)--[7 Ohm]--+
    |                       |                      |
    |                   [5 Ohm]                  (+)
    |                   shared                    10V
    |                       |                    (-)
    |                       |                      |
    +---[2 Ohm]------------+----------------------+
         Mesh 1                   Mesh 2
```

**Input:**

```
Enter no of Meshes : 2
Enter the total no of Current sources in the circuit (if no current source enter 0(zero)) : 0
Mesh 1
Enter the values of all resistors(Ex: 2,5,10) : 3,5,2
Mesh 2
Enter the values of all resistors(Ex: 2,5,10) : 5,7
Mesh 1
Enter the values of all voltage sources(in C.W)[Ex: -5,10,20] : 20,-5
Mesh 2
Enter the values of all voltage sources(in C.W)[Ex: -5,10,20] : 10
Enter the no.of Common resistors B/W Meshes : 1

Enter Common resistance values B/W meshes :
Mesh 1 and Mesh 2 = 5
```

**Output:**

```
 Mesh Currents :
Mesh 1  -->  i1 = 1.97 A in (CW)
Mesh 2  -->  i2 = 1.65 A in (CW)

Current through common resistors :
I-R12(5 Ohm) = 0.32 A (in the direction of i1)
```

**Verification (KVL):**

Mesh 1: $10 i_1 - 5 i_2 = 15$ (net voltage: $20 + (-5) = 15$)

Mesh 2: $-5 i_1 + 12 i_2 = 10$

Solving: $i_1 \approx 1.97\ \text{A},\quad i_2 \approx 1.65\ \text{A}$

---

### Example 5 -- Two Meshes with a Current Source

**Circuit:** Two meshes sharing a 4 Ohm resistor. Mesh 1 has a 20V voltage source and resistors 2 Ohm, 4 Ohm. Mesh 2 contains a **5A current source** (flowing clockwise) and a 6 Ohm resistor along with the shared 4 Ohm resistor.

When a mesh contains a current source, the mesh current for that loop is directly constrained by the source value. No KVL equation is written for that mesh; instead $i_2 = -I_s$ is used.

```
    +---[ 2 Ohm ]---+---[ 6 Ohm ]---+
    |                |                |
  (+)            [ 4 Ohm ]        (5A source)
   20V           (shared)           CW
  (-)                |                |
    |                |                |
    +----------------+----------------+
       Mesh 1 (i1)     Mesh 2 (i2)
```

**Input:**

```
Enter no of Meshes : 2
Enter the total no of Current sources in the circuit (if no current source enter 0(zero)) : 1
Mesh 1
Enter the value of current source in Mesh 1 (in C.W) : 0
Enter the values of all resistors(Ex: 2,5,10) : 2,4
Mesh 2
Enter the value of current source in Mesh 2 (in C.W) : 5
Enter the values of all resistors(Ex: 2,5,10) : 4,6
Mesh 1
Enter the values of all voltage sources(in C.W)[Ex: -5,10,20] : 20
Mesh 2
Enter the values of all voltage sources(in C.W)[Ex: -5,10,20] : 0
Enter the no.of Common resistors B/W Meshes : 1

Enter Common resistance values B/W meshes :
Mesh 1 and Mesh 2 = 4
```

**Output:**

```
 Mesh Currents :
Mesh 1  -->  i1 = 6.67 A in (CW)
Mesh 2  -->  i2 = 5.0 A in (CW)

Current through common resistors :
I-R12(4 Ohm) = 1.67 A (in the direction of i1)
```

**Verification:**

Mesh 2 is constrained: $i_2 = 5\ \text{A}$.

Mesh 1 KVL: $6 i_1 - 4 i_2 = 20 \implies 6 i_1 = 40 \implies i_1 \approx 6.67\ \text{A}$

Current through shared resistor: $i_1 - i_2 = 1.67\ \text{A}$ (direction of $i_1$).

---

## Project Structure

```
mesh_analysis/
|-- Mesh_solver.py        # Main solver script (single-file application)
|-- requirements.txt      # Python dependency list
|-- README.md             # Project documentation
|-- .gitignore            # Git ignore rules
```

### Module Layout (inside `Mesh_solver.py`)

| Section | Description |
|---|---|
| **Constants** | ANSI color codes, unit symbols |
| **Global Data Stores** | Resistor/voltage/current tracking lists and dictionaries |
| `collect_resistors()` | Prompts and stores resistor values per mesh |
| `collect_voltages()` | Prompts and stores voltage source values per mesh |
| `collect_common_resistors()` | Prompts and stores shared resistor values between mesh pairs |
| `build_kvl_equation_terms()` | Constructs KVL string terms from `mesh_elements` |
| `solve_mesh_equations()` | Converts terms to SymPy equations and solves the linear system |
| `compute_common_resistor_currents()` | Calculates branch currents through shared resistors |
| `remove_duplicate_pairs()` | Filters duplicate common-resistor entries (e.g., R12 vs R21) |
| `display_instructions()` | Prints formatted usage instructions |
| `display_mesh_currents()` | Prints solved mesh currents with CW/A.CW direction |
| `display_common_resistor_currents()` | Prints current through shared branches with flow direction |
| **Main Program** | Orchestrates input, solving, and output in four sequential steps |

---

## Future Improvements

- **Web interface** -- Flask/Streamlit front-end for browser-based circuit input and visualization.
- **Graphical circuit diagrams** -- Auto-generate circuit schematics from input data using `matplotlib` or `schemdraw`.
- **Matrix display** -- Show the assembled resistance matrix and voltage vector before solving.
- **Export results** -- Output solutions to CSV, JSON, or PDF report format.
- **Input validation** -- Robust error handling for malformed or inconsistent circuit data.
- **Supermesh support** -- Automatic supermesh detection when a current source is shared between two meshes.
- **Unit tests** -- Automated test suite with known circuit solutions for regression testing.

---

## Author

**M. Abhiram**

B.Tech Engineering Student

| | |
|---|---|
| Originally Developed | 1st Year B.Tech |
| Refactored & Improved | 3rd Year B.Tech |

---

## License

MIT License

Copyright (c) 2026 M. Abhiram

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
