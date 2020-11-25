from z3.z3util import BoolRef, And
from typing import *
from dataclasses import dataclass

from syntax import *
from z3types import *
from parse import *

@dataclass(frozen=True)
class ProgramState:
    pc: int
    state_condition: Expr
    memory: FrozenSet[Tuple[Variable, Expr]]

def convert_state(state: ProgramState) -> Callable[[Z3State], BoolRef]:
    pc = state.pc
    state_condition = state.state_condition
    memory = state.memory

    def state_func(variables: Z3State) -> BoolRef:
        old_variables, new_variables = variables
        new_var_dict = dict(new_variables)

        parsed_condition = parse_expr(state_condition, new_variables)
        parsed_memory = { v: parse_expr(expr, old_variables) for v, expr in memory }

        return And(new_var_dict[PC] == state.pc,
                   parsed_condition,
                   *(new_var_dict[v] == expr for v, expr in parsed_memory.items()))

    return state_func

