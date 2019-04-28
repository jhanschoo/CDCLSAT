from __future__ import annotations
from typing import List, Tuple, TYPE_CHECKING

from brancher import Brancher

if TYPE_CHECKING:
  from shared_types import Literal, Value, Variable
  from propagating_formula import PropagatingFormula
  from assignment import Assignment

class ArbitraryBrancher(Brancher):

  @staticmethod
  def create(formula: PropagatingFormula) -> Brancher:
    return ArbitraryBrancher(formula)

  def __init__(self: ArbitraryBrancher, formula: PropagatingFormula) -> None:
    self.decision_count = 0
    return None

  def record_resolved_lit(self, lit: Literal):
    pass

  def record_learned_clause(self, clause: List[Literal]):
    pass

  def make_decision(self, assignment: Assignment) -> Tuple[Variable, Value]:
    self.decision_count += 1
    unassigned_variables = assignment.get_unassigned()
    return (next(iter(unassigned_variables)), 0)