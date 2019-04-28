from __future__ import annotations
from brancher import Brancher
from typing import Tuple, TYPE_CHECKING
import random

if TYPE_CHECKING:
  from shared_types import Value, Variable
  from propagating_formula import PropagatingFormula
  from assignment import Assignment

class RandomBrancher(Brancher):

  @staticmethod
  def create(formula: PropagatingFormula) -> Brancher:
    return RandomBrancher(formula)

  def __init__(self: RandomBrancher, formula: PropagatingFormula) -> None:
    return None

  def make_decision(self, assignment: Assignment) -> Tuple[Variable, Value]: # TODO: implement
    unassigned_variables = list(assignment.get_unassigned())
    return (random.choice(unassigned_variables), 0)
