import yaml
from utils.dict_utils import dotdict
from task_4.qaoa_gate_based import PennylaneMIS_QAOA
from pennylane import numpy as np

config = yaml.safe_load(open("config.yml"))
config = dotdict(config)

def gate_based_solver(config):
    """
    Solve the Maximum Independent Set (MIS) problem using gate-based Quantum Approximate Optimization Algorithm (QAOA).

    Args:
        config (dotdict): Configuration parameters for QAOA solver.

    Returns:
        None
    """
    # Initialize the QAOA solver
    solver = PennylaneMIS_QAOA(
        config.QAOA_LAYER_PARAMS,
        config.QAOA_LAYER_DEPTH,
        config.SIMULATOR,
        config.STEPS,
    )
    solver.set_nx_graph_to_solve(config.NUM_NODES, config.EDGES_PROBS, config.SEED)

    if config.DRAW_GRAPH:
        solver.draw_graph("Generated Graph")

    # Solve the MIS problem
    solver.solve(logs_file=config.LOGS_FILE)

    # Postprocessing
    probs = solver.get_probabilities()
    ans = np.argmax(probs)
    ans_nodes = bin(ans)[2:]
    solver.set_mis_nodes(ans_nodes)
    solver.draw_graph("MIS nodes (in green)", with_mis_nodes=True)


if __name__ == "__main__":

    # Sanity check on QAOA type
    allowed_qaoa_types = ["GATE-BASED", "ADIABATIC"]
    assert (
        config.QAOA_TYPE in allowed_qaoa_types
    ), f"Unknown QAOA_TYPE: {config.QAOA_TYPE}. Must be one of {allowed_qaoa_types}."

    if config.QAOA_TYPE == "GATE-BASED":
        gate_based_solver(config)
