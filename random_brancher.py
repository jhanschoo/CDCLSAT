from __future__ import annotations
from typing import List, Tuple, TYPE_CHECKING
import random

from brancher import Brancher

if TYPE_CHECKING:
  from shared_types import Literal, Value, Variable
  from propagating_formula import PropagatingFormula
  from assignment import Assignment

class RandomBrancher(Brancher):

  @staticmethod
  def create(formula: PropagatingFormula) -> Brancher:
    return RandomBrancher(formula)

  def __init__(self: RandomBrancher, formula: PropagatingFormula) -> None:
    return None

  def record_resolved_lit(self, lit: Literal):
    pass

  def record_learned_clause(self, clause: List[Literal]):
    pass

  def make_decision(self, assignment: Assignment) -> Tuple[Variable, Value]:
    unassigned_variables = list(assignment.get_unassigned())
    return (random.choice(unassigned_variables), 0)
