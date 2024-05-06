import numpy as np
import networkx as nx


def convert_to_qubo(graph):
    """Converts an undirected graph to a QUBO matrix.

    Args:
      graph: A networkx graph.

    Returns:
      A QUBO matrix.
    """

    # Create a QUBO matrix with one qubit for each vertex in the graph.
    qubo = np.zeros((graph.number_of_nodes(), graph.number_of_nodes()))

    # For each edge in the graph, add a penalty term to the QUBO matrix.
    for edge in graph.edges():
        i, j = edge
        qubo[i, j] += 20
        qubo[j, i] += 20

    for i in range(graph.number_of_nodes()):
        qubo[i, i] -= 10

    qubo[qubo==0] = 0

    return qubo


if __name__ == "__main__":
    # Example usage:

    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (1, 2), (2, 3)])

    qubo = convert_to_qubo(graph)

    print(qubo)
