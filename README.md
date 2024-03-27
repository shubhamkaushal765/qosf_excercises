# qsof_excercises

The MIS problem aims to find the largest set of nodes in a graph such that no two nodes in the set are adjacent.

## Graph Utils

### Star Graph
```python
from mis_solver import mis, get_mis_problem

# Generate the graph and MIS problem
graph, mis_problem = get_mis_problem()

# Solve the MIS problem
solver = pyo.SolverFactory('glpk')
solver.solve(mis_problem)

# Extract the solution
solution = [node for node in graph.nodes if pyo.value(mis_problem.x[node]) > 0]
print("Maximum Independent Set:", solution)
```