from z3.z3util import Solver, Int, Exists, And
from itertools import chain

from syntax import *
from model import *
from state import *
from z3types import *
from typing import Set

def solve_ag(model: Z3Model, p: Callable[[Z3Variables], BoolRef], variables: List[Variable]):
    solver = Solver()
    k = model.state_count()

    s = [ frozenset( { var: Int(f"{var}__{i}") for var in variables }.items() ).union(
          frozenset( { (PC, Int(f"__pc__{i}")) } ) ) for i in range(k+1)  ]
    s_unfolded = [ z3var for var, z3var in chain(*s) ]
    print(s_unfolded)

    after_exists_part = And(*(model.exists_state((s[i-1], s[i])) for i in range(1, k+1)),
                            model.exists_initial((s[0], s[1])),
                            *(model.exists_transition((s[i-1], s[i]), (s[i], s[i+1])) for i in range(1, k)),
                            Not(p(s[k])))

    solver.add(Exists(s_unfolded, after_exists_part))

    print(after_exists_part)
    print(solver.check())


