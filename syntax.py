from typing import *
from enum import Enum, auto
from dataclasses import dataclass

Variable = NewType("Variable", str)
PC = Variable("__reserved__pc__variable__")

class UnaryOp(Enum):
    NOT = auto()
    
class BinomialOp(Enum):
    ADD = auto()
    SUBTRACT = auto()
    MULTIPLY = auto()
    REMAINDER = auto()
    AND = auto()
    OR = auto()
    EQ = auto()
    NEQ = auto()
    GT = auto()
    GE = auto()
    LT = auto()
    LE = auto()

@dataclass(frozen=True)
class UnaryExpr:
    type: UnaryOp
    operand: "Expr"
    
@dataclass(frozen=True)
class BinomialExpr:
    type: BinomialOp
    lhs: "Expr"
    rhs: "Expr"

Expr = Union[Variable, UnaryExpr, BinomialExpr, int, bool]

@dataclass(frozen=True)
class IfStmt:
    condition: Expr
    then_body: List["Stmt"]
    else_body: List["Stmt"]

@dataclass(frozen=True)
class AssignStmt:
    lhs: Variable
    rhs: Expr

@dataclass(frozen=True)
class WhileStmt:
    condition: Expr
    body: List[Any]
    
Stmt = Union[IfStmt, AssignStmt]
 
