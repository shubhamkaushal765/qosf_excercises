# Notes <!-- omit from toc -->

## Table of Contents <!-- omit from toc -->
- [QAOA - PennyLane](#qaoa---pennylane)
  - [Overview](#overview)
    - [QAOA Algorithm](#qaoa-algorithm)
    - [Code Structure](#code-structure)
  - [Usage](#usage)
  - [References](#references)
- [Quantum Adiabatic Algorithm](#quantum-adiabatic-algorithm)
  - [Overview](#overview-1)
    - [The `AdiabaticMIS` class](#the-adiabaticmis-class)
  - [Usage](#usage-1)
  - [References](#references-1)


## QAOA - PennyLane

### Overview

The `qaoa.py` file contains a Python implementation of the Quantum Approximate Optimization Algorithm (QAOA) using PennyLane for solving the Maximum Independent Set (MIS) problem on a graph. The MIS problem is an NP-hard problem that involves finding the largest subset of vertices in a graph such that no two vertices in the subset are adjacent.

#### QAOA Algorithm
The Quantum Approximate Optimization Algorithm (QAOA) is a hybrid quantum-classical algorithm for solving combinatorial optimization problems. It works by encoding the problem into a cost Hamiltonian and applying alternating layers of cost and mixer Hamiltonians to a quantum state.

#### Code Structure

- `PennylaneMIS_QAOA` class: This class represents the QAOA algorithm for solving the MIS problem. It provides methods for setting up the QAOA circuit, solving the MIS problem using QAOA, getting the probabilities of all possible states, setting the MIS nodes based on the solution, and visualizing the graph and solution.
- `qaoa_layer` function: This function applies a single QAOA layer, consisting of a cost layer and a mixer layer.
- `circuit` function: This function constructs the QAOA circuit by applying the Hadamard gate to all qubits and then applying the QAOA layers.
- `solve` function: This function solves the MIS problem using QAOA. It optimizes the QAOA layer parameters using gradient descent and saves the optimization logs to a file.
- `get_probs` function: This function computes and returns the probabilities of all possible states after running the QAOA circuit.
- `set_mis_nodes` function: This function sets the nodes belonging to the maximum independent set based on a given bitstring.
- `draw_graph` function: This function visualizes the graph, with an option to highlight the MIS nodes

### Usage

```python
# Input variables
num_nodes = 10  # Set the desired number of nodes in the graph
device = "qulacs.simulator"  # Set the PennyLane device to be used
distance_multiplier = 8  # Set the distance multiplier for node coordinates

# Create an instance of the PennylaneMIS_QAOA class
solver = PennylaneMIS_QAOA(num_nodes, device, distance_multiplier)

# QAOA variables to solve and save
qaoa_layer_params = [0.5, 0.5, 0.5, 0.5]  # Initial QAOA layer parameters
qaoa_layer_depth = 2  # Depth of QAOA layers
steps = 50  # Number of optimization steps
logs_file = "logs.csv"  # File to save the optimization logs

# Solve the MIS problem using QAOA
solver.solve(qaoa_layer_params, qaoa_layer_depth, steps, logs_file)

# Get the probabilities of all possible states
probs = solver.get_probs(draw_graph=True)

# Set the MIS nodes based on the solution
nodes_bitstring = "010101"  # Example bitstring representing the MIS nodes
solver.set_mis_nodes(nodes_bitstring)

# Draw the graph with MIS nodes highlighted
solver.draw_graph(title="MIS Solution", with_mis_nodes=True)
```

### References

- [Pennylane demo on QAOA](https://pennylane.ai/search/?q=qaoa&contentType=DEMO)
- [QAOA GitHub Tutorial - Pennylane](https://github.com/PennyLaneAI/qml/blob/master/demonstrations/tutorial_qaoa_intro.py)
- [Docs on Pennylane's MIS implementation](https://docs.pennylane.ai/en/stable/code/api/pennylane.qaoa.cost.max_independent_set.html)
- [Extremely Good Introduction for QAOA with Pennylane - YT](https://www.youtube.com/watch?v=cMZcA2SQnYQ)

## Quantum Adiabatic Algorithm

The `adiabatic.py` file contains a Python implementation of an adiabatic quantum algorithm for solving the Maximum Independent Set (MIS) problem on a graph.

### Overview

The adiabatic quantum algorithm used in this implementation is based on the principles of quantum annealing. It involves evolving the quantum system from an easily solvable initial state to the desired final state by slowly changing the Hamiltonian of the system.

The algorithm works as follows:

- The graph representing the MIS problem is converted to a register of atomic qubits with their coordinates.
- An adiabatic pulse is defined, which includes a Rabi frequency waveform and a detuning waveform that evolve over time.
- A sequence is created, and the adiabatic pulse is added to the sequence.
- The sequence is simulated using the QutipEmulator, which performs the adiabatic quantum evolution.
- The final state of the simulation is sampled, and the most common final states (representing the MIS solutions) are reported.

#### The `AdiabaticMIS` class

This class represents the adiabatic quantum algorithm for solving the MIS problem. It inherits from the MISGraph class and provides methods for converting the QUBO problem to a register of atomic qubits, solving the MIS problem using the adiabatic quantum algorithm, and visualizing the graph and solution.


### Usage

- Creat an instance of the `AdiabaticMIS` class with the specified number of nodes. The graph is generated and can be accessed using `AdiabaticMIS.graph`.
- Solve the MIS problem using the adiabatic quantum algorithm.
- Set the MIS nodes based on the adiabatic solution.
- Draws the graph with the MIS nodes highlighted.

```python
num_nodes = 7
solver = AdiabaticMIS(num_nodes)

# # Solve the MIS problem using the adiabatic quantum algorithm
counts = solver.solve(draw_plots=True).most_common(3)
ans = counts[0][0] # fetching the most occurred bitstring

# Print the adiabatic solution
print(f"Adiabatic Solution: {counts}")

# Set the MIS nodes and draw the graph with the solution
solver.set_mis_nodes(ans)
solver.draw_graph(title="Adiabatic Solution", with_mis_nodes=True)
```

### References
- [Pulser - QAOA and QAA to solve a QUBO problem](https://pulser.readthedocs.io/en/stable/tutorials/qubo.html)