from syntax import *

from z3types import *
from z3.z3util import And, Or, Not
from typing import *

def parse_expr(expr: Expr, variables: Z3Variables) -> Z3Ref:
    if isinstance(expr, UnaryExpr):
        if expr.type == UnaryOp.NOT:
            return Not(parse_expr(expr.operand, variables))
        else:
            raise Exception("Invalid unary operator")

    elif isinstance(expr, BinomialExpr):
        lhs = expr.lhs
        rhs = expr.rhs
        
        if expr.type == BinomialOp.ADD:
            return parse_expr(lhs, variables) + parse_expr(rhs, variables)
        elif expr.type == BinomialOp.SUBTRACT:
            return parse_expr(lhs, variables) - parse_expr(rhs, variables)
        elif expr.type == BinomialOp.MULTIPLY:
            return parse_expr(lhs, variables) * parse_expr(rhs, variables)
        elif expr.type == BinomialOp.REMAINDER:
            return parse_expr(lhs, variables) % parse_expr(rhs, variables)
        elif expr.type == BinomialOp.AND:
            return And(parse_expr(lhs, variables), parse_expr(rhs, variables))
        elif expr.type == BinomialOp.OR:
            return Or(parse_expr(lhs, variables), parse_expr(rhs, variables))
        elif expr.type == BinomialOp.EQ:
            return parse_expr(lhs, variables) == parse_expr(rhs, variables)
        elif expr.type == BinomialOp.NEQ:
            return parse_expr(lhs, variables) != parse_expr(rhs, variables)
        elif expr.type == BinomialOp.GT:
            return parse_expr(lhs, variables) > parse_expr(rhs, variables)
        elif expr.type == BinomialOp.GE:
            return parse_expr(lhs, variables) >= parse_expr(rhs, variables)
        elif expr.type == BinomialOp.LT:
            return parse_expr(lhs, variables) < parse_expr(rhs, variables)
        elif expr.type == BinomialOp.LE:
            return parse_expr(lhs, variables) <= parse_expr(rhs, variables)
        else:
            raise Exception("Invalid binary operator")

    elif isinstance(expr, str): # Variable
        return dict(variables).get(expr)

    else:
        return expr

