import networkx as nx
import matplotlib.pyplot as plt


class MISGraph:
    def __init__(self):
        # Graph variables
        self.num_nodes = None
        self.edge_probs = None
        self.seed = None
        self.graph = None
        self.mis_nodes = None

    def set_nx_graph(self, num_nodes, edge_probs, seed):
        """Set up the graph to solve MIS.

        Args:
            num_nodes (int): Number of nodes in the graph.
            edge_probs (float): Probability of edge creation.
            seed (int): Random seed for graph generation.
        """
        # graph variables
        self.num_nodes = num_nodes
        self.edge_probs = edge_probs
        self.seed = seed

        # nx.graph to solve MIS with QAOA
        self.graph = nx.fast_gnp_random_graph(n=num_nodes, p=edge_probs, seed=seed)

    def set_mis_nodes(self, nodes_bitstring):
        """Set the nodes belonging to the maximum independent set.

        Args:
            nodes_bitstring (str): Bitstring representing the MIS nodes.
        """
        self.mis_nodes = "0" * (self.num_nodes - len(nodes_bitstring)) + nodes_bitstring

    def draw_graph(self, title=None, with_mis_nodes=False, plot_wait_time=None):
        """Draw the graph.

        Args:
            title (str, optional): Title for the plot. Defaults to None.
            with_mis_nodes (bool, optional): Whether to highlight MIS nodes. Defaults to False.
        """

        mis_flags = self.mis_nodes
        if with_mis_nodes == True:

            # sanity checks
            assert mis_flags is not None, "MIS nodes not specified."
            assert len(mis_flags) == len(
                self.graph
            ), f"Length of MIS node bitstring: {mis_flags} does not match \
                number of nodes in the graph: {self.num_nodes}."

            color_map = list(map(int, mis_flags))
            color_map = [["lightblue", "green"][i] for i in color_map]

        else:
            color_map = ["lightblue" for _ in range(self.num_nodes)]

        plt.figure()
        if title is not None:
            plt.title(title)
        nx.draw_kamada_kawai(self.graph, node_color=color_map, with_labels=True)
        if plot_wait_time:
            plt.show(block=False)
            plt.pause(plot_wait_time)
            plt.close()
        else:
            plt.show()
