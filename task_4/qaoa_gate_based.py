from datetime import datetime
import pandas as pd
import sys, yaml
from tqdm import tqdm

sys.path.append(".")

from utils.graph_utils import get_random_graph
from utils.dict_utils import dotdict

config = yaml.safe_load(open("config.yml"))
config = dotdict(config)

import pennylane as qml
from pennylane import qaoa
from pennylane import numpy as np


class PennylaneMIS_QAOA:
    def __init__(self, qaoa_layer_depth, device, steps=50):

        # graph variables
        self.num_nodes = None
        self.edge_probs = None
        self.seed = None
        self.draw_graph = False

        # QAOA variables
        self.qaoa_layer_depth = qaoa_layer_depth
        self.steps = steps
        self.optimizer = qml.GradientDescentOptimizer()
        ## The grond state of the cost_h is the solution.
        ## mixer_h and cost_h does not commute.
        self.cost_h, self.mixer_h = None, None

        # setting up simulating device
        self.dev = None
        self.device = device

    def set_nx_graph_to_solve(self, num_nodes, edge_probs, seed, draw_graph=False):

        # graph variables
        self.num_nodes = num_nodes
        self.edge_probs = edge_probs
        self.seed = seed
        self.draw_graph = draw_graph

        # nx.graph to solve MIS with QAOA
        self.graph = get_random_graph(
            num_nodes=num_nodes, p_edge=edge_probs, seed=seed, draw_graph=draw_graph
        )

        # define the cost and mixer hamiltonian based on the given graph
        self.cost_h, self.mixer_h = qaoa.cost.max_independent_set(self.graph)
        self.dev = qml.device(self.device, wires=self.num_nodes)

    def qaoa_layer(self, gamma, alpha):
        qaoa.cost_layer(gamma, self.cost_h)
        qaoa.mixer_layer(alpha, self.mixer_h)

    def circuit(self, params, **kwargs):
        for wire in range(self.num_nodes):
            qml.Hadamard(wires=wire)
        qml.layer(
            self.qaoa_layer, self.qaoa_layer_depth, params[0], params[1]
        )

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


if __name__ == "__main__":
    solver = PennylaneMIS_QAOA(config.QAOA_LAYER_DEPTH, config.SIMULATOR, config.STEPS)
    solver.set_nx_graph_to_solve(
        config.NUM_NODES, config.EDGES_PROBS, config.SEED, config.DRAW_GRAPH
    )
    solver.solve(logs_file=config.LOGS_FILE)
