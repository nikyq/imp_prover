from syntax import *
from parse import *
from ltl import *
from model import *
from state import *
from convert import *
from z3types import *

from z3 import *

# def to_model(statements: List[Stmt], variables: List[Variable]) -> ProgramModel:

def unwind_test():
    a = Variable("a")
    b = Variable("b")
    variables = [ a, b ]
    
    statements = [
        AssignStmt(lhs = a, rhs = 1),
        AssignStmt(lhs = b, rhs = 2),
        AssignStmt(lhs = a, rhs = BinomialExpr(BinomialOp.MULTIPLY, a, -1)),
        WhileStmt(condition = BinomialExpr(BinomialOp.LT, a, b),
                  body = [
                      AssignStmt(lhs = a, rhs = BinomialExpr(BinomialOp.ADD, a, b))
                  ]),
        AssignStmt(lhs = b, rhs = BinomialExpr(BinomialOp.SUBTRACT, BinomialExpr(BinomialOp.ADD, a, b), 2))
    ]

    print(label_statements(unwind_loops(statements)))


def to_model_test():
    a = Variable("a")
    b = Variable("b")
    variables = [ a, b ]
    
    statements = [
        AssignStmt(lhs = a, rhs = 1),
        AssignStmt(lhs = b, rhs = 2),
        AssignStmt(lhs = a, rhs = BinomialExpr(BinomialOp.MULTIPLY, a, -1)),
        IfStmt(condition = BinomialExpr(BinomialOp.LT, a, b),
               then_body = [
                   AssignStmt(lhs = a, rhs = BinomialExpr(BinomialOp.ADD, a, b))
               ],
               else_body = [
                   AssignStmt(lhs = b, rhs = BinomialExpr(BinomialOp.MULTIPLY, b, 2))
               ]),
        AssignStmt(lhs = b, rhs = BinomialExpr(BinomialOp.SUBTRACT, BinomialExpr(BinomialOp.ADD, a, b), 2))
    ]

    statements = [
        AssignStmt(lhs = a, rhs = 1),
        AssignStmt(lhs = b, rhs = 2),
    ]

    model = to_model(preprocess(statements), variables)
    #print(list(model.transitions))
    return model

def convert_test(m):
    pc0, a0, b0, pc1, a1, b1, pc2, a2, b2 = Ints("pc0 a0 b0 pc1 a1 b1 pc2 a2 b2")

    v0 = frozenset( { PC: pc0, Variable("a"): a0, Variable("b"): b0 }.items() )
    v1 = frozenset( { PC: pc1, Variable("a"): a1, Variable("b"): b1 }.items() )
    v2 = frozenset( { PC: pc2, Variable("a"): a2, Variable("b"): b2 }.items() )

    print(convert_model(m).state_exists((v0,v1)))
    print(convert_model(m).initial_state_exists((v0,v1)))
    print(convert_model(m).transition_exists((v0,v1), (v1, v2)))

def solve_test(m):
    a, b = Variable("a"), Variable("b")
    variables = [ a, b ]
    # def solve_ag(model: Z3Model, p: Callable[[Z3Variables], BoolRef], variables: List[Variable], k: int):

    def p(z3var):
        return dict(z3var)[a] > 0
    solve_ag(m, p, variables)

m = to_model_test()
#convert_test(m)
solve_test(m)

#unwind_test()
