import networkx as nx
import matplotlib.pyplot as plt


def get_random_graph(num_nodes=8, p_edge=0.4, draw_graph=True, seed=12345):
    """
    Generate a random graph using the fast G(n,p) model from NetworkX.

    Parameters:
    - num_nodes (int): Number of nodes in the graph.
    - p_edge (float): Probability of an edge between any pair of nodes.
    - draw_graph (bool): Whether to visualize the graph.

    Returns:
    nx.Graph: The generated random graph.
    """
    graph = nx.fast_gnp_random_graph(n=num_nodes, p=p_edge, seed=seed)
    return graph
