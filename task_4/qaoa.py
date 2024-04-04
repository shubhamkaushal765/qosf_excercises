from datetime import datetime
import pandas as pd
import sys
from tqdm import tqdm
import matplotlib.pyplot as plt

sys.path.append(".")

from .mis import MISGraph
from utils.graph_utils import get_square_graph

import networkx as nx
import pennylane as qml
from pennylane import qaoa
from pennylane import numpy as np


class PennylaneMIS_QAOA(MISGraph):
    """
    A class for solving the Maximum Independent Set (MIS) problem using the Quantum Approximate Optimization Algorithm (QAOA) with PennyLane.

    The MIS problem is an NP-hard problem that involves finding the largest subset of vertices in a graph such that no two vertices in the subset are adjacent.

    This class provides methods for setting up the QAOA circuit, solving the MIS problem using QAOA, getting the probabilities of all possible states, setting the MIS nodes based on the solution, and visualizing the graph and solution.
    """

    def __init__(
        self,
        num_nodes=None,
        graph=None,
        device="qulacs.simulator",
    ):
        """
        Initialize the QAOA solver for the MIS problem.

        Args:
            num_nodes (int): The number of nodes in the graph.
            graph (networkx graph): The networkx graph to solve.
            device (str, optional): The PennyLane device to be used for simulations. Defaults to "qulacs.simulator".

        Note: Only one of [num_nodes, graph] argument must be specified.
        """
        condition = (num_nodes is not None and graph is None) or (  # num_node is given
            num_nodes is None and graph is not None  # graph is given
        )
        assert condition, "Only one of [num_nodes, graph] argument must be specified."

        super().__init__()

        # Graph variables
        if num_nodes is not None:
            self.num_nodes = num_nodes
            self.graph, self.coords = get_square_graph(self.num_nodes)
        elif graph is not None:
            self.graph = graph
            self.num_nodes = len(self.graph)
        self.mis_nodes = None

        # QAOA variables
        ## Define the Hamiltonians and device based on the given graph
        self.cost_h, self.mixer_h = qaoa.cost.max_independent_set(self.graph)
        self.optimizer = qml.GradientDescentOptimizer()

        ## Setting up the simulation device
        self.device = device
        self.dev = qml.device(self.device, wires=self.num_nodes)

    def qaoa_layer(self, gamma, alpha):
        """
        Apply a single QAOA layer consisting of a cost layer and a mixer layer.

        Args:
            gamma (array-like): Parameters for the cost layer.
            alpha (array-like): Parameters for the mixer layer.
        """
        qaoa.cost_layer(gamma, self.cost_h)
        qaoa.mixer_layer(alpha, self.mixer_h)

    def circuit(self, params, **kwargs):
        """
        Construct the QAOA circuit by applying the Hadamard gate to all qubits and then applying the QAOA layers.

        Args:
            params (array-like): Parameters for the QAOA circuit (gamma and alpha values).
        """
        for wire in range(self.num_nodes):
            qml.Hadamard(wires=wire)
        qml.layer(self.qaoa_layer, self.qaoa_layer_depth, params[0], params[1])

    def solve(
        self,
        qaoa_layer_params=[0.5, 0.5, 0.5, 0.5],
        qaoa_layer_depth=2,
        steps=50,
        logs_file=None,
    ):
        """
        Solve the MIS problem using the QAOA algorithm.

        Args:
            qaoa_layer_params (list or array-like, optional): Initial parameters for the QAOA layers. Defaults to [0.5, 0.5, 0.5, 0.5].
            qaoa_layer_depth (int, optional): Depth of the QAOA layers. Defaults to 2.
            steps (int, optional): Number of optimization steps. Defaults to 50.
            logs_file (str, optional): Path to a file where the optimization logs will be saved. Defaults to None.
        """

        # Sanity checks
        assert self.cost_h is not None, "Cost Hamiltonian is not defined."
        assert self.mixer_h is not None, "Mixer Hamiltonian is not defined."

        self.qaoa_layer_depth = qaoa_layer_depth
        self.steps = steps

        @qml.qnode(self.dev)
        def cost_function(params):
            """
            Cost function for the optimization problem.

            Args:
                params (array-like): Parameters for the QAOA circuit (gamma and alpha values).

            Returns:
                float: The value of the cost function.
            """
            self.circuit(params)
            return qml.expval(self.cost_h)

        # Initialize parameters
        self.params = np.reshape(qaoa_layer_params, (2, 2), requires_grad=True)
        params = self.params

        # Solve and save optimization logs
        df = pd.DataFrame({"Timestamp": [], "Step": [], 0: [], 1: [], 2: [], 3: []})
        df.loc[len(df.index)] = [datetime.now(), 0] + params.flatten().tolist()

        for i in tqdm(range(1, self.steps + 1)):
            params = self.optimizer.step(cost_function, params)
            self.params = params
            if logs_file is not None:
                df.loc[len(df.index)] = [datetime.now(), i] + params.flatten().tolist()
                df.to_csv(logs_file)

    def get_probs(self, draw_graph=True, plot_wait_time=None):
        """
        Get the probabilities of all possible states after running the QAOA circuit.

        Args:
            draw_graph (bool, optional): Whether to draw a bar plot of the probability distribution. Defaults to True.

        Returns:
            numpy.ndarray: An array of probabilities for all possible states.
        """

        wires = range(self.num_nodes)

        @qml.qnode(self.dev)
        def probability_circuit(gamma, alpha):
            """
            Quantum circuit to compute the probabilities of all possible states.

            Args:
                gamma (array-like): Parameters for the cost layer.
                alpha (array-like): Parameters for the mixer layer.

            Returns:
                numpy.ndarray: An array of probabilities for all possible states.
            """
            self.circuit([gamma, alpha])
            return qml.probs(wires=wires)

        probs = probability_circuit(self.params[0], self.params[1])
        if draw_graph:
            plt.figure()
            plt.title("Probability Distribution")
            plt.style.use("ggplot")
            plt.bar(range(2 ** len(wires)), probs)
            if plot_wait_time:
                plt.show(block=False)
                plt.pause(plot_wait_time)
                plt.close()
            else: plt.show()
        return probs

    def set_mis_nodes(self, nodes_bitstring):
        """
        Set the nodes belonging to the maximum independent set based on a given bitstring.

        Args:
            nodes_bitstring (str): A bitstring representing the MIS nodes, where '1' indicates a node is part of the MIS, and '0' indicates it is not.
        """
        self.mis_nodes = "0" * (self.num_nodes - len(nodes_bitstring)) + nodes_bitstring


def main(num_nodes):

    solver = PennylaneMIS_QAOA(num_nodes)
    solver.draw_graph("Generated Graph")
    solver.solve(steps=50, logs_file=f"logs_{num_nodes}.txt")
    probs = solver.get_probs()
    ans = np.argmax(probs)
    ans_nodes = bin(ans)[2:]
    solver.set_mis_nodes(ans_nodes)
    solver.draw_graph("MIS nodes (in green)", with_mis_nodes=True)


if __name__ == "__main__":
    nodes = [3, 5, 6, 7][1:]
    for n in nodes:
        main(n)
