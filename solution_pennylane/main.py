import sys
from datetime import datetime
import pandas as pd
from tqdm import tqdm

sys.path.append(".")

from graph_utils import get_random_graph
import pennylane as qml
from pennylane import qaoa
from pennylane import numpy as np

NUM_NODES = 8
EDGES_PROBS = 0.4
QAOA_LAYER_DEPTH = 2


def main():
    graph = get_random_graph(
        num_nodes=NUM_NODES, p_edge=EDGES_PROBS, seed=42, draw_graph=False
    )
    cost_h, mixer_h = qaoa.cost.max_independent_set(graph)
    # print("cost Hamiltonian:", cost_h)
    # print("mixer Hamiltonian:", mixer_h)

    def qaoa_layer(gamma, alpha):
        qaoa.cost_layer(gamma, cost_h)
        qaoa.mixer_layer(alpha, mixer_h)

    def circuit(params, **kwargs):
        for wire in range(NUM_NODES):
            qml.Hadamard(wires=wire)
        qml.layer(qaoa_layer, QAOA_LAYER_DEPTH, params[0], params[1])

    print("################################", "Simulation")

    dev = qml.device("qulacs.simulator", wires=NUM_NODES)

    @qml.qnode(dev)
    def cost_function(params):
        circuit(params)
        return qml.expval(cost_h)

    optimizer = qml.GradientDescentOptimizer()
    steps = 50
    params = np.array([[0.5, 0.5], [0.5, 0.5]], requires_grad=True)

    df = pd.DataFrame({"Timestamp": [], "Step": [], 0: [], 1: [], 2: [], 3: []})
    df.loc[len(df.index)] = [datetime.now(), 0] + params.flatten().tolist()

    for i in tqdm(range(1, steps + 1)):
        params = optimizer.step(cost_function, params)
        df.loc[len(df.index)] = [datetime.now(), i] + params.flatten().tolist()
        df.to_csv("logs.csv")

    print("Optimal Parameters")
    print(params)


if __name__ == "__main__":
    main()


"""
Step: 5
[[0.53204145 0.50495833]
 [0.5306348  0.55254305]]
Step: 20
[[0.64766214 0.51431999]
 [0.61988455 0.71638737]]
Step: 25
[[0.69308484 0.51638703]
 [0.64906866 0.77351621]]
"""
