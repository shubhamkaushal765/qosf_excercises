from datetime import datetime
import pandas as pd
import sys, yaml
from tqdm import tqdm
import matplotlib.pyplot as plt
import networkx as nx

sys.path.append(".")

from utils.dict_utils import dotdict

config = yaml.safe_load(open("config.yml"))
config = dotdict(config)

import pennylane as qml
from pennylane import qaoa
from pennylane import numpy as np


class PennylaneMIS_QAOA:
    def __init__(self, qaoa_layer_params, qaoa_layer_depth, device, steps=50):

        # graph variables
        self.num_nodes = None
        self.edge_probs = None
        self.seed = None
        self.graph = None
        self.mis_nodes = None

        # QAOA variables
        self.qaoa_layer_depth = qaoa_layer_depth
        self.steps = steps
        self.optimizer = qml.GradientDescentOptimizer()
        ## The grond state of the cost_h is the solution.
        ## mixer_h and cost_h does not commute.
        self.cost_h, self.mixer_h = None, None
        self.params = np.reshape(qaoa_layer_params, (2, 2))

        # setting up simulating device
        self.dev = None
        self.device = device

    def set_nx_graph_to_solve(self, num_nodes, edge_probs, seed):

        # graph variables
        self.num_nodes = num_nodes
        self.edge_probs = edge_probs
        self.seed = seed

        # nx.graph to solve MIS with QAOA
        self.graph = nx.fast_gnp_random_graph(n=num_nodes, p=edge_probs, seed=seed)

        # define the cost and mixer hamiltonian based on the given graph
        self.cost_h, self.mixer_h = qaoa.cost.max_independent_set(self.graph)
        self.dev = qml.device(self.device, wires=self.num_nodes)

    def qaoa_layer(self, gamma, alpha):
        qaoa.cost_layer(gamma, self.cost_h)
        qaoa.mixer_layer(alpha, self.mixer_h)

    def circuit(self, params, **kwargs):
        for wire in range(self.num_nodes):
            qml.Hadamard(wires=wire)
        qml.layer(self.qaoa_layer, self.qaoa_layer_depth, params[0], params[1])

    def solve(self, logs_file=None):

        # sanity checks
        assert self.cost_h is not None
        assert self.mixer_h is not None

        @qml.qnode(self.dev)
        def cost_function(params):
            self.circuit(params)
            return qml.expval(self.cost_h)

        # initialization
        params = np.array([[0.5, 0.5], [0.5, 0.5]], requires_grad=True)

        # solving and saving
        df = pd.DataFrame({"Timestamp": [], "Step": [], 0: [], 1: [], 2: [], 3: []})
        df.loc[len(df.index)] = [datetime.now(), 0] + params.flatten().tolist()

        for i in tqdm(range(1, self.steps + 1)):
            params = self.optimizer.step(cost_function, params)
            if logs_file is not None:
                df.loc[len(df.index)] = [datetime.now(), i] + params.flatten().tolist()
                df.to_csv(logs_file)

    def get_probabilities(self):

        wires = range(self.num_nodes)

        @qml.qnode(self.dev)
        def probability_circuit(gamma, alpha):
            self.circuit([gamma, alpha])
            return qml.probs(wires=wires)

        probs = probability_circuit(self.params[0], self.params[1])
        plt.style.use("ggplot")
        plt.bar(range(2 ** len(wires)), probs)
        plt.show()
        return probs

    def set_mis_nodes(self, nodes_bitstring):
        self.mis_nodes = nodes_bitstring

    def draw_graph(self, title=None, with_mis_nodes=False):

        mis_flags = self.mis_nodes
        if with_mis_nodes == False:
            mis_flags = "0" * self.num_nodes

        # sanity checks
        assert mis_flags is not None, "MIS nodes not specified."
        assert len(mis_flags) == len(
            self.graph
        ), "Length of MIS node bitstring does not match number of nodes in the graph."

        color_map = list(map(int, mis_flags))
        color_map = [["lightblue", "green"][i] for i in color_map]
        plt.figure()
        if title is not None:
            plt.title(title)
        nx.draw_kamada_kawai(self.graph, node_color=color_map, with_labels=True)
        plt.show()


if __name__ == "__main__":
    solver = PennylaneMIS_QAOA(
        config.QAOA_LAYER_PARAMS,
        config.QAOA_LAYER_DEPTH,
        config.SIMULATOR,
        config.STEPS,
    )
    solver.set_nx_graph_to_solve(config.NUM_NODES, config.EDGES_PROBS, config.SEED)

    if config.DRAW_GRAPH:
        solver.draw_graph("Generated Graph")

    # solver.solve(logs_file=config.LOGS_FILE)
    probs = solver.get_probabilities()
    ans = np.argmax(probs)
    ans_nodes = bin(ans)[-config.NUM_NODES :]
    solver.set_mis_nodes(ans_nodes)
    solver.draw_graph("MIS nodes (in green)", with_mis_nodes=True)
