"""
https://pulser.readthedocs.io/en/stable/tutorials/qubo.html#Quantum-Adiabatic-Algorithm
"""

import numpy as np
import matplotlib.pyplot as plt
from pulser import Pulse, Sequence, Register
from pulser_simulation import QutipEmulator
from pulser.devices import DigitalAnalogDevice
from pulser.waveforms import InterpolatedWaveform
from scipy.optimize import minimize
from scipy.spatial.distance import pdist, squareform
import networkx as nx
from utils.graph_utils import convert_to_qubo
from utils.dict_utils import plot_distribution
from task_4.mis import MISGraph


class AdiabaticMIS(MISGraph):
    def __init__(self):
        super().__init__()

        self.qubo = None

    def set_qubo(self, num_nodes, edge_probs, seed):
        super().set_nx_graph(num_nodes, edge_probs, seed)
        assert self.graph is not None
        self.qubo = convert_to_qubo(self.graph)

    def classical_solution_to_qubo(self):

        assert self.qubo is not None, "The QUBO matrix cannot be None."

        Q = self.qubo

        bitstrings = [np.binary_repr(i, len(Q)) for i in range(2 ** len(Q))]
        costs = []
        # this takes exponential time with the dimension of the QUBO
        for b in bitstrings:
            z = np.array(list(b), dtype=int)
            cost = z.T @ Q @ z
            costs.append(cost)
        zipped = zip(bitstrings, costs)
        sort_zipped = sorted(zipped, key=lambda x: x[1])
        return sort_zipped[:3]

    def convert_qubo_2_atomic_reg(self):
        # Q = self.qubo

        # def evaluate_mapping(new_coords, *args):
        #     """Cost function to minimize. Ideally, the pairwise
        #     distances are conserved"""
        #     Q, shape = args
        #     new_coords = np.reshape(new_coords, shape)
        #     new_Q = squareform(
        #         DigitalAnalogDevice.interaction_coeff / pdist(new_coords) ** 6
        #     )
        #     return np.linalg.norm(new_Q - Q)

        # shape = (len(Q), 2)
        # costs = []
        # np.random.seed(0)
        # x0 = np.random.random(shape).flatten()
        # res = minimize(
        #     evaluate_mapping,
        #     x0,
        #     args=(Q, shape),
        #     method="Nelder-Mead",
        #     tol=1e-6,
        #     options={"maxiter": 200000, "maxfev": None},
        # )
        # coords = np.reshape(res.x, (len(Q), 2))

        # coords
        coords = np.array([0, 0, 0, 1, 1, 0, 1, 1, 1, 2]).reshape(-1, 2) * 8
        qubits = dict(enumerate(coords))
        reg = Register(qubits)
        reg.draw(
            blockade_radius=DigitalAnalogDevice.rydberg_blockade_radius(2),
            draw_graph=False,
            draw_half_radius=True,
        )
        return reg

    def solve(self, draw_plots=True):
        Q = self.qubo
        reg = self.convert_qubo_2_atomic_reg()

        Omega = np.median(Q[Q > 0].flatten()) / 10
        delta_0 = -5  # just has to be negative
        delta_f = -delta_0  # just has to be positive
        T = 4000

        adiabatic_pulse = Pulse(
            InterpolatedWaveform(T, [1e-9, Omega, 1e-9]),
            InterpolatedWaveform(T, [delta_0, 0, delta_f]),
            0,
        )

        seq = Sequence(reg, DigitalAnalogDevice)
        seq.declare_channel("ising", "rydberg_global")
        seq.add(adiabatic_pulse, "ising")
        if draw_plots:
            seq.draw()

        simul = QutipEmulator.from_sequence(seq)
        results = simul.run()
        final = results.get_final_state()
        count_dict = results.sample_final_state()

        if draw_plots:
            plot_distribution(count_dict)

        return count_dict


if __name__ == "__main__":
    num_nodes = 8
    edge_probs = 0.2
    seed = 42

    solver = AdiabaticMIS()
    solver.set_qubo(num_nodes, edge_probs, seed)
    solver.draw_graph(title="Generated Graph")

    # classically solving the QUBO matrix
    classical_sols = solver.classical_solution_to_qubo()
    print(f"Classical solutions: {classical_sols}")

    # Adiabatic solver
    counts = solver.solve(draw_plots=True).most_common(3)
    ans = counts[0][0]  # [::-1]
    print(f"Adiabatic Solution: {counts}")

    solver.set_mis_nodes(ans)

    solver.draw_graph(title="Adiabatic Solution", with_mis_nodes=True)
