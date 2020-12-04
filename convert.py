from functools import reduce

from model import *
from syntax import *
from parse import *
from dataclasses import dataclass, replace
from z3 import *

def unwind(statement: WhileStmt, k: int) -> IfStmt:
    condition = statement.condition
    body: List[Stmt] = statement.body

    fallback = IfStmt(condition = condition, then_body = [], else_body = [])

    stmts = [ body ] * k
    to_if: Callable[[IfStmt, List[Stmt]], IfStmt] = lambda stmt, stmts: IfStmt(condition = condition, then_body = [ *stmts, stmt ], else_body = [])

    return reduce(to_if, stmts, fallback)

def unwind_loops(statements: List[Stmt], k:int = 4) -> List[Stmt]:
    return [ unwind(stmt, k) if isinstance(stmt, WhileStmt) else stmt for stmt in statements ]

def label_statements(statements: List[Stmt]) -> List[Stmt]:
    pc = 1

    def label(statements: List[Stmt]) -> List[Stmt]:
        nonlocal pc # 사이드이펙트 없이 간편하게 처리하는 방법이 떠오르지 않네요
        results: List[Stmt] = []

        for stmt in statements:
            new_stmt = replace(stmt, pc = pc)
            if isinstance(stmt, IfStmt):
                new_then_body = label(stmt.then_body)
                new_else_body = label(stmt.else_body)
                new_stmt = replace(new_stmt, then_body = new_then_body, else_body = new_else_body)
            results.append(new_stmt)
            pc += 1

        return results

    return label(statements)

def make_state(memory: FrozenSet[Tuple[Variable, Expr]]) -> Z3FuncState:
    def state_func(z3state: Z3State) -> BoolRef:
        prev_variables, next_variables = z3state
        pv_dict, nv_dict = dict(prev_variables), dict(next_variables)
        memory_dict = dict(memory)

        return And( *( nv_dict[v] == parse_expr(memory_dict[v], prev_variables) for v in memory_dict.keys() ) )

    return state_func

StatesSetTuple = Tuple[FrozenSet[Z3FuncState], FrozenSet[Transition]]

def connect_state_sets(state: Z3FuncState, heads: FrozenSet[Z3FuncState], state_sets: StatesSetTuple, condition: Callable[[Z3Variables], BoolLike]):
#     def convert_transition(transition: Tuple[ProgramState, ProgramState]) ->  Callable[[Z3State, Z3State], BoolRef]:
#         state1, state2 = transition
#         state_func1, state_func2 = convert_state(state1), convert_state(state2)
#         return lambda variables_pair1, variables_pair2: And(state_func1(variables_pair1), state_func2(variables_pair2))
        
    make_transition = lambda s1, s2: Transition(condition = conditon, state_func = lambda v1, v2: And( s1(v1), s2(v2) ))
    s, r = state_sets

    new_s = s.union({state}) 
    new_r = r.union(frozenset(make_transition(condition = condition, states = make_transition(state, head)) for head in heads))
    
    return new_s, new_r

def collect_sets(statements: List[Stmt], variables: List[Variable]) -> Tuple[FrozenSet[Z3FuncState], StatesSetTuple]:
    if len(statements) == 0:
        return frozenset(), (frozenset(), frozenset())
    else:
        stmt = statements[0]

    memory_dict: dict[Variable, Expr] = { v: v for v in variables }
    if isinstance(stmt.pc, int):
        memory_dict[PC] = stmt.pc
    else:
        raise Exception(f"PC Variable not initialized correctly - {stmt.pc}")
        
    if isinstance(stmt, IfStmt):
        if_true_state = make_state(frozenset(memory_dict.items()))
        if_false_state = make_state(frozenset(memory_dict.items()))
        state_condition = stmt.condition
        parsed_condition: Callable[[Z3Variables], BoolLike] = lambda variables: parse_expr(state_condition, variables)
        
        if_true_heads, if_true_sets = collect_sets(stmt.then_body + statements[1:], variables)
        if_false_heads, if_false_sets = collect_sets(stmt.else_body + statements[1:], variables)

        true_s, true_r = connect_state_sets(if_true_state, if_true_heads, if_true_sets, parsed_condition)
        false_s, false_r = connect_state_sets(if_false_state, if_false_heads, if_false_sets, Not(parsed_condition))

        return frozenset((if_true_state, if_false_state)), (true_s.union(false_s), true_r.union(false_r))

    elif isinstance(stmt, AssignStmt):
        memory_dict[stmt.lhs] = stmt.rhs
        state = make_state(frozenset(memory_dict.items()))
        heads, next_state_sets = collect_sets(statements[1:], variables)
        new_s, new_r = connect_state_sets(state, heads, next_state_sets, lambda variables: True)
        return frozenset([state]), (new_s, new_r)
    else:
        raise Exception("Invalid statement type")

def preprocess(statements: List[Stmt]):
    return label_statements(unwind_loops(statements))

def to_model(statements: List[Stmt], variables: List[Variable]):
    heads, state_sets = collect_sets(statements, variables)

    memory_dict: dict[Variable, Expr] = { v: v for v in variables }
    memory_dict[PC] = 0
    empty_state = make_state(frozenset(memory_dict.items()))

    states, transitions = connect_state_sets(empty_state, heads, state_sets, lambda variables: True)

    return Z3Model(initial_states = heads, states = states, transitions = transitions)
    
# def to_model(statements: List[Stmt], variables: List[Variable]) -> ProgramModel:
#     heads, state_sets = collect_sets(statements, variables, pc = 1)
# 
#     memory_dict: dict[Variable, Expr] = { v: v for v in variables }
#     empty_state = ProgramState(pc = 0, state_condition = True, memory = frozenset(memory_dict.items()))
#     final_s, final_r = connect_state_sets(empty_state, heads, state_sets)
# 
#     s_kset = KSet(final_s)
#     i_kset = KSet(heads)
#     r_kpairset = KSet(final_r)
# 
#     return ProgramModel(states = s_kset, initial_states = i_kset, transitions = r_kpairset)
# 
