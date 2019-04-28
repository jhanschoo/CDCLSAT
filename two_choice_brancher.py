from __future__ import annotations
from typing import Dict, List, Tuple, TYPE_CHECKING
import random

from brancher import Brancher

if TYPE_CHECKING:
  from shared_types import Literal, Value, Variable
  from propagating_formula import PropagatingFormula
  from assignment import Assignment

class TwoChoiceBrancher(Brancher):

  @staticmethod
  def create(formula: PropagatingFormula) -> Brancher:
    return TwoChoiceBrancher(formula)

  def __init__(self: TwoChoiceBrancher, formula: PropagatingFormula) -> None:
    Brancher.__init__(self)
    raw_formula = formula.formula.formula
    var_counts: Dict[Variable, int] = {}
    for clause in raw_formula:
      raw_clause = clause.clause
      for literal in raw_clause:
        if not var_counts.get(abs(literal)):
          var_counts[abs(literal)] = 0
      if len(raw_clause) != 2:
        for literal in raw_clause:
          var_counts[abs(literal)] += 1
    self.scores = var_counts

  def record_resolved_lit(self, lit: Literal):
    pass

  def record_learned_clause(self, clause: List[Literal]):
    pass

  def make_decision(self, assignment: Assignment) -> Tuple[Variable, Value]:
    self.decision_count += 1
    unassigned_variables = list(assignment.get_unassigned())
    max_vars: List[Variable] = []
    max_count = 0
    for var in unassigned_variables:
      if self.scores[var] > max_count:
        max_vars = [var]
        max_count = self.scores[var]
      elif self.scores[var] == max_count:
        max_vars.append(var)
    return (random.choice(max_vars), random.choice((0, 1)))
