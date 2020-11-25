from z3 import *
from z3.z3 import ArithRef, BoolRef
from typing import *
from enum import Enum, auto

# constructs
# if
# for
# assignment
# arithmetic
# logical
# variable
# constant (literal)

# input & output은 여전히 동일

# Constructs

Z3Ref = Union[ArithRef, BoolRef, int, bool]
BoolLike = Union[BoolRef, bool]
ArithLike= Union[ArithRef, int]
  
class State(NamedTuple):
    pc: int
    memory: FrozenSet[Tuple[Z3Ref, Z3Ref]]
    variables: FrozenSet[Tuple[Variable, Z3Ref]]

def solve_ag():
    pass

class Graph(NamedTuple):
    adj_arr: List[Tuple[BoolLike, State, State]]
    head: State

def parse_expr(expr, variables):
    return expr(variables)

def make_relations(statements: List[Stmt], prev_state: State, prev_variables: Dict[Variable, Z3Ref]) -> Optional[Graph]:
    if statements == []:
        return None

    stmt = statements[0]
    z3_variables : Dict[Variable, Z3Ref] = { Variable(var): Int(f"{var}__{prev_state.pc + 1}") for var, p in prev_variables.items() }
    memory : Dict[Z3Ref, Z3Ref] = { new_var: prev_variables[Variable(k)] for k, new_var in z3_variables.items() } 

    if isinstance(stmt, IfStmt):
        cond = parse_expr(stmt.condition, z3_variables)
        state = State(pc = prev_state.pc + 1, memory = frozenset(memory.items()), variables = frozenset(z3_variables.items()))
        then_graph = make_relations(stmt.then_body + statements[1:], state, z3_variables)
        else_graph = make_relations(stmt.else_body + statements[1:], state, z3_variables)

        new_graph = []

        if then_graph is not None:
            new_graph += then_graph.adj_arr
            new_graph.append((cond, state, then_graph.head))
        if else_graph is not None:
            new_graph += else_graph.adj_arr
            new_graph.append((Not(cond), state, else_graph.head))

        return Graph(adj_arr = new_graph, head = state)

    elif isinstance(stmt, AssignStmt):
        lhs = stmt.lhs
        rhs = parse_expr(stmt.rhs, prev_variables)

        target_var = z3_variables[lhs]
        memory[target_var] = rhs

        state = State(pc = prev_state.pc + 1, memory = frozenset(memory.items()), variables = frozenset(z3_variables.items()))
        next_graph = make_relations(statements[1:], state, z3_variables)

        new_graph = []
        if next_graph is not None:
            new_graph += next_graph.adj_arr
            new_graph.append((True, state, next_graph.head))

        return Graph(adj_arr = new_graph, head = state)

    else:
        raise Exception("Invalid statement type")

def relations(statements: List[Stmt], variables: List[Variable]):
    pc = 0
    init_variables = { var: Int(f"{var}__{pc}") for var in variables }
    memory = { z3v: Int(f"{v}__before_i") for v, z3v in init_variables.items() }
    state = State(pc = pc, memory = frozenset(memory.items()), variables = frozenset(init_variables.items()))

    return make_relations(statements, state, init_variables)

def solve_ag(statements, variables, condition_to_test):
    s = Solver()

    # I
    relations_graph = relations(statements, variables)
    head_cnf = And(*[ lhs == rhs for lhs, rhs in relations_graph.head.memory ])
    s.add(head_cnf)
    
    # R
    for cond, src_state, dest_state in relations_graph.adj_arr:
        src_cnf = And(*[ lhs == rhs for lhs, rhs in src_state.memory ])
        dest_cnf = And(*[ lhs == rhs for lhs, rhs in dest_state.memory ])
        s.add(And(cond, src_cnf, dest_cnf))

    # P
    states = set([s for c, s, d in relations_graph.adj_arr] + [d for c, s, d in relations_graph.adj_arr])
    condition_test_list = []

    for state in states:
        state_cnf = And(*[ lhs == rhs for lhs, rhs in state.memory ])
        cond_cnf = Not(condition_to_test(dict(state.variables)))
        condition_test_list.append(And(state_cnf, cond_cnf))

    s.add(Or(*condition_test_list))
    print(s)
    print(s.check())

a = Variable("a")
b = Variable("b")

variables = [ a, b ]
statements: List[Stmt] = [
    AssignStmt(lhs = a, rhs = lambda v: 1),
    AssignStmt(lhs = b, rhs = lambda v: 2),
    AssignStmt(lhs = a, rhs = lambda v: v[a] * (-1)),
    IfStmt(condition = lambda v: v[a] < v[b],
           then_body = [
               AssignStmt(lhs = a, rhs = lambda v: v[a] + v[b])
           ],
           else_body = [
               AssignStmt(lhs = b, rhs = lambda v: v[b] * 2)
           ]),
    AssignStmt(lhs = b, rhs = lambda v: v[a] + v[b] - 2) 
]

solve_ag(statements, variables, lambda v: v[a] < 0)

