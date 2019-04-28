from __future__ import annotations
from typing import List, Tuple, TYPE_CHECKING

from abc import ABC, abstractmethod

if TYPE_CHECKING:
  from shared_types import Literal, Value, Variable
  from propagating_formula import PropagatingFormula
  from assignment import Assignment

class Brancher(ABC):
  
  @staticmethod
  @abstractmethod
  def create(formula: PropagatingFormula) -> Brancher:
    pass

  @abstractmethod
  def record_resolved_lit(self, lit: Literal):
    pass

  @abstractmethod
  def record_learned_clause(self, clause: List[Literal]):
    pass

  @abstractmethod
  def make_decision(self, assignment: Assignment) -> Tuple[Variable, Value]: # : implement
    pass