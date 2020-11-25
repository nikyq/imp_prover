from z3.z3util import *
from typing import *
from syntax import *

Z3Ref = Union[ArithRef, BoolRef, int, bool]
BoolLike = Union[BoolRef, bool]
ArithLike= Union[ArithRef, int]

Z3Variables = FrozenSet[Tuple[Variable, Z3Ref]]
Z3State = Tuple[Z3Variables, Z3Variables]
