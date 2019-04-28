from __future__ import annotations
from brancher import Brancher
from typing import Tuple, TYPE_CHECKING

if TYPE_CHECKING:
  from shared_types import Value, Variable
  from propagating_formula import PropagatingFormula
  from assignment import Assignment

class ArbitraryBrancher(Brancher):

  @staticmethod
  def create(formula: PropagatingFormula) -> Brancher:
    return ArbitraryBrancher(formula)

  def __init__(self: ArbitraryBrancher, formula: PropagatingFormula) -> None:
    return None

  def make_decision(self, assignment: Assignment) -> Tuple[Variable, Value]:
    unassigned_variables = assignment.get_unassigned()
    return (next(iter(unassigned_variables)), 0)