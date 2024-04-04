import math
import numpy as np
from scipy.spatial.distance import euclidean
import networkx as nx
import matplotlib.pyplot as plt


def get_square_graph(num_nodes):
    """
    Generate a square graph with the given number of nodes.
    
    Args:
        num_nodes (int): The number of nodes in the graph.
        
    Returns:
        G (NetworkX Graph): The generated square graph.
        coords (list): A list of node coordinates.
    """

    # Calculate the edge length of the square grid
    edge_length = math.ceil(np.sqrt(num_nodes))

    # Generate coordinates for the nodes on the square grid
    coords = coords = np.array(
        [(r, c) for r in range(edge_length) for c in range(edge_length)]
    )[:num_nodes]

    # Generate edges between nodes within a distance of 1.5 units
    edges = []
    coords_enum = list(enumerate(coords))
    for i, vi in coords_enum:
        for j, vj in coords_enum:
            if j <= i:
                continue
            if euclidean(vi, vj) < 1.5:
                edges.append((i, j))

    # Create a NetworkX graph
    G = nx.Graph()
    G.add_nodes_from(range(num_nodes))
    G.add_edges_from(edges)

    return G, coords


if __name__ == "__main__":
    for n in [3, 5, 6, 7]:
        get_square_graph(n)
