# 🔍 Mesh Analysis in Python

A Python program to perform **Mesh Analysis** for electrical circuits using the **SymPy** library.  
It calculates mesh currents for circuits containing **resistors**, **voltage sources**, and **current sources**, and supports **multiple meshes** with **common resistors**.

---

## ✅ Features
✔ Supports **multiple meshes**  
✔ Handles **resistors, voltage sources, and current sources**  
✔ Calculates:
- Mesh currents
- Current through common resistors  
✔ Interactive **command-line interface**  
✔ **Color-coded instructions** (using `colorama`)  
✔ Cross-platform (Windows, Linux, macOS)  

---

## 🔧 Requirements
- Python 3.8 or higher
- [SymPy](https://www.sympy.org/)
- [colorama](https://pypi.org/project/colorama/)

Install dependencies:
```
In bash run
pip install sympy colorama
```
## Usage

Run the script:
python mesh_analysis.py

You will see instructions like this:

!! INSTRUCTIONS !!
(1) Enter resistance and voltage values separated by commas (Ex: 2,3,4)
(2) For voltage/current sources, enter with sign (+ CW, - ACW)
(3) Units: Resistance in Ohm, Voltage in V, Current in A
(4) Assume all mesh currents are in CW direction

MESH ANALYSIS

--Example Run
Enter number of meshes: 2
Enter total number of current sources (0 if none): 0

Mesh 1
Enter resistor values (Ex: 2,5,10): 2,4
Mesh 2
Enter resistor values (Ex: 2,5,10): 3,6

Mesh 1
Enter voltage source values (Ex: -5,10,20): 10
Mesh 2
Enter voltage source values (Ex: -5,10,20): -5

Enter number of common resistors between meshes: 1
Enter common resistance values between meshes:
Mesh 1 and Mesh 2 = 2

Example Output
Mesh Currents:
Mesh 1 --> i1 = 3.33 A (CW)
Mesh 2 --> i2 = 1.67 A (A.CW)

📂 Project Structure
mesh_analysis.py    # Main program file
README.md           # Documentation
