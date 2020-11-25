from __future__ import annotations
from typing import *
from abc import ABC, abstractmethod
from z3.z3util import BoolRef, Or, And
from dataclasses import dataclass

from z3types import *
from state import ProgramState, convert_state

T = TypeVar("T")
class AbstractKSet(ABC, Generic[T]):
    @abstractmethod
    def has(self, item: T) -> BoolLike:
        pass


class AbstractKPairSet(ABC, Generic[T]):
    @abstractmethod
    def has(self, item1: T, item2: T) -> BoolLike:
        pass


class KSet(AbstractKSet, Generic[T]):
    def __init__(self, source_set: FrozenSet[T]):
        self.source_set = source_set
        
    def has(self, item: T):
        return item in self.source_set

    def __iter__(self):
        return iter(self.source_set)

    def __len__(self):
        return len(self.source_set)


class KPairSet(AbstractKPairSet, Generic[T]):
    def __init__(self, source_set: FrozenSet[Tuple[T,T]]):
        self.source_set = source_set
        
    def has(self, item: T):
        return item in self.source_set

    def __iter__(self):
        return iter(self.source_set)

    def __len__(self):
        return len(self.source_set)


class Z3Set(AbstractKSet[Z3Variables]):
    def __init__(self, source_set: FrozenSet[Callable[[Z3State], BoolRef]]):
        self.source_set = source_set
        
    def has(self, item: Z3State) -> BoolRef:
        return Or(*(state_func(item) for state_func in self.source_set))

    def __iter__(self):
        return iter(self.source_set)

    def __len__(self):
        return len(self.source_set)
        

class Z3PairSet(AbstractKSet[Z3Variables]):
    def __init__(self, source_set: FrozenSet[Callable[[Z3State, Z3State], BoolRef]]):
        self.source_set = source_set
        
    def has(self, item1: Z3State, item2: Z3State) -> BoolRef:
        return Or(*(state_func(item1, item2) for state_func in self.source_set))

    def __iter__(self):
        return iter(self.source_set)

    def __len__(self):
        return len(self.source_set)


T = TypeVar("T")
S = TypeVar("S")
R = TypeVar("R")

@dataclass(frozen=True)
class KripkeStruct(Generic[T, S, R]):
    states: 'S[T]'
    initial_states: 'S[T]'
    transitions: 'R[T]'

ProgramModel = KripkeStruct[ProgramState, KSet, KPairSet]
Z3Model = KripkeStruct[Z3State, Z3Set, Z3PairSet]

def convert_model(model: ProgramModel) -> Z3Model:
    def convert_transition(transition: Tuple[ProgramState, ProgramState]) ->  Callable[[Z3State, Z3State], BoolRef]:
        state1, state2 = transition
        state_func1, state_func2 = convert_state(state1), convert_state(state2)
        return lambda variables_pair1, variables_pair2: And(state_func1(variables_pair1), state_func2(variables_pair2))
        
    new_states = frozenset(convert_state(state) for state in model.states)
    new_initial_states = frozenset(convert_state(state) for state in model.initial_states)
    new_transitions = frozenset(convert_transition(transition) for transition in model.transitions)

    return Z3Model(states = Z3Set(new_states), initial_states = Z3Set(new_initial_states), transitions = Z3PairSet(new_transitions))
