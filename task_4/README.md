# Notes <!-- omit from toc -->

## Table of Contents <!-- omit from toc -->
- [QAOA - PennyLane](#qaoa---pennylane)
  - [Overview](#overview)
  - [Usage](#usage)
  - [References](#references)
- [Quantum Adiabatic Algorithm](#quantum-adiabatic-algorithm)
  - [Overview](#overview-1)
    - [The `AdiabaticMIS` class](#the-adiabaticmis-class)
  - [Usage](#usage-1)
  - [References](#references-1)


## QAOA - PennyLane

### Overview

The QAOA algorithm is a variational quantum algorithm designed to solve combinatorial optimization problems. In the context of the MIS problem, QAOA aims to find the maximum independent set of vertices in a graph.

### Usage

```python
from PennylaneMIS_QAOA import PennylaneMIS_QAOA

# Initialize the solver
solver = PennylaneMIS_QAOA(qaoa_layer_params, qaoa_layer_depth, device, steps)

# Set the Networkx Graph
solver.set_nx_graph_to_solve(num_nodes, edge_probs, seed)

# Solving MIS
solver.solve(logs_file="logs.csv")

# Visualize the Results: this method gives a histogram of the probabilities.
probs = solver.get_probabilities()

# Visualize the graph nodes
solver.draw_graph(title="Generated Graph", with_mis_nodes=True)
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