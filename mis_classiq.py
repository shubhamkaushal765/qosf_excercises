"""
https://docs.classiq.io/latest/user-guide/built-in-algorithms/combinatorial-optimization/problem-solving/
"""

from classiq.applications.combinatorial_optimization import (
    QAOAConfig,
)
from classiq import construct_combinatorial_optimization_model
from graph_utils.star_graph import get_mis_problem

mis_problem = get_mis_problem()


# Construct a Classiq model for this optimization problem with the construct_combinatorial_optimization_model function.
qaoa_config = QAOAConfig(num_layers=3)
mis_model = construct_combinatorial_optimization_model(
    pyo_model=mis_problem, qaoa_config=qaoa_config
)

# Results
from classiq import synthesize, show
from classiq import execute
import pandas as pd
from classiq.applications.combinatorial_optimization import (
    get_optimization_solution_from_pyo,
)

mis_quantum_program = synthesize(mis_model)
show(mis_quantum_program)
res = execute(mis_quantum_program).result()


vqe_result = res[0].value
solution = get_optimization_solution_from_pyo(
    mis_problem, vqe_result=vqe_result, penalty_energy=qaoa_config.penalty_energy
)
optimization_result = pd.DataFrame.from_records(solution)
result = optimization_result.sort_values(by="cost", ascending=False).head(5)

print(result)