import yaml
from utils.dict_utils import dotdict
from task_4.qaoa import PennylaneMIS_QAOA
from task_4.adiabatic import AdiabaticMIS
from pennylane import numpy as np
import networkx as nx

config = yaml.safe_load(open("config.yml"))
config = dotdict(config)


def qaoa_solver(config):
    """
    Solve the Maximum Independent Set (MIS) problem using the gate-based Quantum Approximate Optimization Algorithm (QAOA).

    Args:
        config (dotdict): Configuration parameters for the QAOA solver.

    Returns:
        None

    This function sets up the QAOA solver based on the provided configuration parameters, solves the MIS problem
    using the QAOA algorithm, and visualizes the generated graph and the solution.
    """

    print("Running the QAOA solver!")

    qaoa_vars = dotdict(config.QAOA_VARS.copy())
    device = qaoa_vars.SIMULATOR

    if qaoa_vars.RANDOM_GRAPH:
        # Generate a random graph
        num_nodes, edge_probs, seed = (
            qaoa_vars.NUM_NODES,
            qaoa_vars.EDGE_PROBS,
            qaoa_vars.SEED,
        )
        graph = nx.fast_gnp_random_graph(n=num_nodes, p=edge_probs, seed=seed)
        solver = PennylaneMIS_QAOA(graph=graph, device=device)
    else:
        # Use a pre-defined graph with the specified number of nodes
        num_nodes = config.NUM_NODES
        solver = PennylaneMIS_QAOA(num_nodes, device=device)

    # Draw the generated graph
    solver.draw_graph("Generated Graph")

    # Solve the MIS problem using the QAOA algorithm
    solver.solve(
        qaoa_layer_params=qaoa_vars.QAOA_LAYER_PARAMS,
        qaoa_layer_depth=qaoa_vars.QAOA_LAYER_DEPTH,
        steps=qaoa_vars.STEPS,  # Note: Using SEED as the number of optimization steps
        logs_file=qaoa_vars.LOG_FILE,
    )

    # Get the probabilities of all possible states
    probs = solver.get_probs(config.DRAW_PLOTS)

    # Get the solution (the state with the highest probability)
    ans = np.argmax(probs)
    ans_nodes = bin(ans)[2:]  # Convert the solution to a bitstring

    # Set the MIS nodes based on the solution
    solver.set_mis_nodes(ans_nodes)

    # Draw the graph with the MIS nodes highlighted
    solver.draw_graph("MIS nodes (in green)", with_mis_nodes=True)


def adiabatic_solver(config):
    """
    Solve the Maximum Independent Set (MIS) problem using the adiabatic quantum algorithm.

    Args:
        config (dotdict): Configuration parameters for the adiabatic solver.

    This function sets up the adiabatic solver based on the provided configuration parameters, solves the MIS problem
    using the adiabatic quantum algorithm, and visualizes the generated graph and the solution.
    """

    print("Running the Adiabatic Solver!")

    num_nodes = config.NUM_NODES
    ada_vars = dotdict(config.ADIABATIC_VARS)

    # Create an instance of the AdiabaticMIS solver
    solver = AdiabaticMIS(num_nodes, ada_vars.DISTANCE_MULTIPLIER)

    # Draw the generated graph
    solver.draw_graph(title="Generated Graph")

    # Solve the MIS problem using the adiabatic quantum algorithm
    counts = solver.solve(
        rabi_f=ada_vars.RABI_FREQUENCY,  # Rabi frequency
        delta_0=ada_vars.DELTA_0,  # Initial detuning
        delta_f=ada_vars.DELTA_F,  # Final detuning
        T=ada_vars.TOTAL_TIME,  # Total time
        draw_plots=config.DRAW_PLOTS,  # Whether to draw plots or not
    ).most_common(3)

    # Get the solution (the state with the highest count)
    ans = counts[0][0]  # [::-1]

    # Print the adiabatic solution
    print(f"Adiabatic Solution: {counts}")

    # Set the MIS nodes based on the solution
    solver.set_mis_nodes(ans)

    # Draw the graph with the MIS nodes highlighted
    solver.draw_graph(title="Adiabatic Solution", with_mis_nodes=True)


if __name__ == "__main__":
    solver = config.SOLVERS
    assert solver in ["QAOA", "Adiabatic", "both"], f"Unknown solver: {solver} given."

    if solver in ["QAOA", "both"]:
        qaoa_solver(config)

    if solver in ["Adiabatic", "both"]:
        adiabatic_solver(config)
