from __future__ import annotations
from typing import Dict, List, Tuple, TYPE_CHECKING
import math

from brancher import Brancher

if TYPE_CHECKING:
  from shared_types import Literal, Value, Variable
  from propagating_formula import PropagatingFormula
  from assignment import Assignment

  Score = int
  Sign = int

class VSIDSBrancher(Brancher):

  @staticmethod
  def create(formula: PropagatingFormula) -> Brancher:
    return VSIDSBrancher(formula)

  def __init__(self: VSIDSBrancher, formula: PropagatingFormula) -> None:
    Brancher.__init__(self)
    raw_formula = formula.formula.formula
    var_counts: Dict[Variable, List[int]] = {}
    for clause in raw_formula:
      raw_clause = clause.clause
      for literal in raw_clause:
        if not var_counts.get(abs(literal)):
          var_counts[abs(literal)] = [0, 0]
        if literal < 0:
          var_counts[abs(literal)][0] += 1
        else:
          var_counts[abs(literal)][1] += 1
    self.scores: Dict[Variable, Score] = {}
    self.sign: Dict[Variable, Sign] = {}
    self.max_score = 0
    for v, counts in var_counts.items():
      sign = 1
      if counts[0] > counts[1]:
        sign = 0
      total_counts = counts[0] + counts[1]
      self.scores[v] = total_counts
      self.sign[v] = sign
      if total_counts > self.max_score:
        self.max_score = total_counts
    self.bonus = self.max_score // 3 + 1

  def record_resolved_lit(self, lit: Literal):
    self.scores[abs(lit)] += self.bonus
    if self.scores[abs(lit)] >= self.max_score:
      self.max_score = self.scores[abs(lit)]
    self._maintenance()
    pass

  def record_learned_clause(self, clause: List[Literal]):
    for lit in clause:
      self.scores[abs(lit)] += self.bonus
      if self.scores[abs(lit)] >= self.max_score:
        self.max_score = self.scores[abs(lit)]
    self._grow_bonus()
    self._maintenance()

  def _maintenance(self):
    if self.max_score > 2**24 or self.bonus > 2**24:
      self.bonus //= 2**16
      for v in self.scores:
        self.scores[v] //=2**16

  def _grow_bonus(self):
    self.bonus = math.ceil(self.bonus * 6 / 5)

  def make_decision(self, assignment: Assignment) -> Tuple[Variable, Value]:
    self.decision_count += 1
    unassigned_variables = assignment.get_unassigned()
    max_var = 0
    max_score = 0
    for var in unassigned_variables:
      if self.scores[var] >= max_score:
        max_var = var
        max_score = self.scores[var]
    return (max_var, self.sign[var])

