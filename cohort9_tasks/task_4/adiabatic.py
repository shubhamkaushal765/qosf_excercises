import numpy as np
from pulser import Pulse, Sequence, Register
from pulser_simulation import QutipEmulator
from pulser.devices import DigitalAnalogDevice
from pulser.waveforms import InterpolatedWaveform
import matplotlib.pyplot as plt
from .mis import MISGraph

import sys

sys.path.append(".")
from utils.dict_utils import plot_distribution
from utils.graph_utils import get_square_graph


class AdiabaticMIS(MISGraph):
    """
    A class that represents an adiabatic quantum algorithm for solving the
    Maximum Independent Set (MIS) problem on a graph.
    """

    def __init__(self, num_nodes, distance_multiplier=8, plot_wait_time=False):
        """
        Initialize the AdiabaticMIS object.

        Args:
            num_nodes (int): The number of nodes in the graph.
            distance_multiplier (float, optional): A multiplier for the node coordinates. Defaults to 8.
        """
        super().__init__()
        self.num_nodes = num_nodes
        self.graph, self.coords = get_square_graph(self.num_nodes)
        self.coords = np.array(self.coords) * distance_multiplier
        self.plot_wait_time = plot_wait_time

    def convert_qubo_2_atomic_reg(self):
        """
        Convert the QUBO problem to a register of atomic qubits with their coordinates.

        Returns:
            Register: A register of atomic qubits with their coordinates.
        """
        # coords
        coords = self.coords
        qubits = dict(enumerate(coords))
        reg = Register(qubits)
        reg.draw(
            blockade_radius=DigitalAnalogDevice.rydberg_blockade_radius(1),
            draw_graph=False,
            draw_half_radius=True,
        )
        if self.plot_wait_time:
            plt.pause(self.plot_wait_time)
            plt.close()
        return reg

    def solve(self, rabi_f=1, delta_0=-5, delta_f=5, T=4000, draw_plots=True):
        """
        Solve the MIS problem using an adiabatic quantum algorithm.

        Args:
            draw_plots (bool, optional): Whether to draw plots or not. Defaults to True.
            rabi_f (float): Rabi frequency
            delta_0 (float): Initial detuning (must be negative)
            delta_f (float): Final detuning (must be positive)
            T (int): Total time

        Returns:
            dict: A dictionary containing the final state counts.
        """
        reg = self.convert_qubo_2_atomic_reg()
        Omega = rabi_f  # Rabi frequency

        # Define the adiabatic pulse
        adiabatic_pulse = Pulse(
            InterpolatedWaveform(T, [1e-9, Omega, 1e-9]),
            InterpolatedWaveform(T, [delta_0, 0, delta_f]),
            0,
        )

        # Create the sequence and add the adiabatic pulse
        seq = Sequence(reg, DigitalAnalogDevice)
        seq.declare_channel("ising", "rydberg_global")
        seq.add(adiabatic_pulse, "ising")

        if draw_plots:
            seq.draw()
            if self.plot_wait_time:
                plt.pause(self.plot_wait_time)
                plt.close()

        # Run the simulation
        simul = QutipEmulator.from_sequence(seq)
        results = simul.run()
        final = results.get_final_state()
        count_dict = results.sample_final_state()

        if draw_plots:
            plot_distribution(count_dict)

        return count_dict


def main(num_nodes):
    solver = AdiabaticMIS(num_nodes)
    # solver.set_qubo(num_nodes, edge_probs, seed)
    solver.draw_graph(title="Generated Graph")

    # Adiabatic solver
    counts = solver.solve(draw_plots=True).most_common(3)
    ans = counts[0][0]  # [::-1]
    print(f"Adiabatic Solution: {counts}")

    solver.set_mis_nodes(ans)

    solver.draw_graph(title="Adiabatic Solution", with_mis_nodes=True)


if __name__ == "__main__":
    nodes = [3, 5, 6, 7]
    for n in nodes:
        main(n)
