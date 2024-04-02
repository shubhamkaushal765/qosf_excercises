import networkx as nx
import pyomo.core as pyo
from pyomo.environ import SolverFactory
import matplotlib.pyplot as plt


def mis(graph: nx.Graph) -> pyo.ConcreteModel:
    """
    Define a maximum independent set (MIS) problem using Pyomo for a given graph.

    Parameters:
    - graph (nx.Graph): The input graph for which the MIS problem is defined.

    Returns:
    pyo.ConcreteModel: A Pyomo model representing the MIS problem.
    """
    problem = pyo.ConcreteModel("mis")
    problem.x = pyo.Var(graph.nodes, domain=pyo.Binary)

    @problem.Constraint(graph.edges)
    def independent_rule(problem, node1, node2):
        return problem.x[node1] + problem.x[node2] <= 1

    problem.cost = pyo.Objective(expr=sum(list(problem.x.values())), sense=pyo.maximize)

    return problem


def get_mis_problem(draw_graph=True):
    """
    Generate a star graph and the corresponding MIS problem.

    Returns:
    tuple: A tuple containing the generated graph and the MIS problem.
    """
    graph = nx.star_graph(4)

    if draw_graph:
        nx.draw(graph)
        plt.show()

    mis_problem = mis(graph)
    return graph, mis_problem


if __name__ == "__main__":
    graph, mis_problem = get_mis_problem(draw_graph=False)

    # Solve the MIS problem
    solver = SolverFactory("glpk")
    solver.solve(mis_problem)

    # Extract the solution
    solution = [node for node in graph.nodes if pyo.value(mis_problem.x[node]) > 0]
    print("Maximum Independent Set:", solution)
