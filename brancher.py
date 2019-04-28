from __future__ import annotations
from typing import Tuple, TYPE_CHECKING

from abc import ABC, abstractmethod

if TYPE_CHECKING:
  from shared_types import Value, Variable
  from propagating_formula import PropagatingFormula
  from assignment import Assignment

class Brancher(ABC):
  
  @staticmethod
  @abstractmethod
  def create(formula: PropagatingFormula) -> Brancher:
    pass

  @abstractmethod
  def make_decision(self, assignment: Assignment) -> Tuple[Variable, Value]: # : implement
    pass