# Notes on using QAOA from PENNYLANE

## Overview

The QAOA algorithm is a variational quantum algorithm designed to solve combinatorial optimization problems. In the context of the MIS problem, QAOA aims to find the maximum independent set of vertices in a graph.

## Usage

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

## References

- [Pennylane demo on QAOA](https://pennylane.ai/search/?q=qaoa&contentType=DEMO)
- [QAOA GitHub Tutorial - Pennylane](https://github.com/PennyLaneAI/qml/blob/master/demonstrations/tutorial_qaoa_intro.py)
- [Docs on Pennylane's MIS implementation](https://docs.pennylane.ai/en/stable/code/api/pennylane.qaoa.cost.max_independent_set.html)
- [Extremely Good Introduction for QAOA with Pennylane - YT](https://www.youtube.com/watch?v=cMZcA2SQnYQ)