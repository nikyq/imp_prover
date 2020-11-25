from z3.z3util import Solver, Int, Exists, And
from itertools import chain

from syntax import *
from model import *
from state import *
from z3types import *
from typing import Set

StatesSetTuple = Tuple[FrozenSet[ProgramState], FrozenSet[Tuple[ProgramState, ProgramState]]]

def connect_state_sets(state: ProgramState, heads: FrozenSet[ProgramState], state_sets: StatesSetTuple):
    s, r = state_sets
    new_s = s.union({state}) 
    new_r = r.union(frozenset((state, head) for head in heads))
    
    return new_s, new_r

def collect_sets(statements: List[Stmt], variables: List[Variable], pc: int) -> Tuple[FrozenSet[ProgramState], StatesSetTuple]:
    memory_dict: dict[Variable, Expr] = { v: v for v in variables }

    if len(statements) == 0:
        return frozenset(), (frozenset(), frozenset())
    else:
        stmt = statements[0]
        
    if isinstance(stmt, IfStmt):
        if_true_state = ProgramState(pc = pc, state_condition = stmt.condition, memory = frozenset(memory_dict.items()))
        if_false_state = ProgramState(pc = pc, state_condition = UnaryExpr(UnaryOp.NOT, stmt.condition), memory = frozenset(memory_dict.items()))

        if_true_heads, if_true_sets = collect_sets(stmt.then_body + statements[1:], variables, pc+1)
        if_false_heads, if_false_sets = collect_sets(stmt.else_body + statements[1:], variables, pc+1)

        true_s, true_r = connect_state_sets(if_true_state, if_true_heads, if_true_sets)
        false_s, false_r = connect_state_sets(if_false_state, if_false_heads, if_false_sets)

        return frozenset((if_true_state, if_false_state)), (true_s.union(false_s), true_r.union(false_r))

    elif isinstance(stmt, AssignStmt):
        memory_dict[stmt.lhs] = stmt.rhs
        state = ProgramState(pc = pc, state_condition = True, memory = frozenset(memory_dict.items()))
        heads, next_state_sets = collect_sets(statements[1:], variables, pc+1)
        new_s, new_r = connect_state_sets(state, heads, next_state_sets)
        return frozenset([state]), (new_s, new_r)

    else:
        raise Exception("Invalid statement type")

def to_model(statements: List[Stmt], variables: List[Variable]) -> ProgramModel:
    heads, state_sets = collect_sets(statements, variables, pc = 1)

    memory_dict: dict[Variable, Expr] = { v: v for v in variables }
    empty_state = ProgramState(pc = 0, state_condition = True, memory = frozenset(memory_dict.items()))
    final_s, final_r = connect_state_sets(empty_state, heads, state_sets)

    s_kset = KSet(final_s)
    i_kset = KSet(heads)
    r_kpairset = KSet(final_r)

    return ProgramModel(states = s_kset, initial_states = i_kset, transitions = r_kpairset)

def solve_ag(model: Z3Model, p: Callable[[Z3Variables], BoolRef], variables: List[Variable]):
    solver = Solver()
    k = len(model.states)

    s = [ frozenset( { var: Int(f"{var}__{i}") for var in variables }.items() ).union(
          frozenset( { (PC, Int(f"__pc__{i}")) } ) ) for i in range(k+1)  ]
    s_unfolded = [ z3var for var, z3var in chain(*s) ]
    print(s_unfolded)

    after_exists_part = And(*(model.states.has((s[i-1], s[i])) for i in range(1, k+1)),
                            model.initial_states.has((s[0], s[1])),
                            *(model.transitions.has((s[i-1], s[i]), (s[i], s[i+1])) for i in range(1, k)),
                            Not(p(s[k])))

    solver.add(Exists(s_unfolded, after_exists_part))

    print(after_exists_part)
    print(solver.check())


