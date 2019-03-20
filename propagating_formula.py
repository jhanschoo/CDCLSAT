from __future__ import annotations
from typing import List, Optional, TextIO, Tuple, TYPE_CHECKING

from formula import Formula

if TYPE_CHECKING:
  from shared_types import DecisionLevel, Literal, Value, Variable
  from assignment import Assignment
  from clause import Clause
  from formula import State

class PropagatingFormula:

  SATISFIED: State = Formula.SATISFIED
  UNRESOLVED: State = Formula.UNRESOLVED
  UNSATISFIED: State = Formula.UNSATISFIED

  def __init__(self: PropagatingFormula, file_object: TextIO) -> None:
    self.formula = Formula(file_object)
    self.decision_level: DecisionLevel = 0
    self.propagate()
    self.decision_history: List[Optional[Tuple[Variable, Value]]] = [None]

  def _sat_variable_value_from_unit_clause(self: PropagatingFormula, clause: Clause) -> Tuple[Variable, Value]:
    head_lit, _ = clause.get_head_tail_lit()
    return abs(head_lit), 0 if head_lit < 0 else 1

  def propagate(self: PropagatingFormula) -> None:
    while self.formula.unit_clauses and self.formula.UNRESOLVED:
      clause = next(iter(self.formula.unit_clauses))
      variable, value = self._sat_variable_value_from_unit_clause(clause)
      self.formula.assign(self.decision_level, variable, value, clause)

  def add_clause(self: PropagatingFormula, clause: List[int]) -> None:
    self.formula.add_clause(clause)

  def assign(self: PropagatingFormula, variable: Variable, value: Value) -> None:
    self.decision_level += 1
    self.formula.assign(self.decision_level, variable, value, None)
    self.decision_history.append((variable, value))
    self.propagate()

  def get_current_state(self: PropagatingFormula) -> State:
    return self.formula.get_current_state()

  def get_current_decision_level(self: PropagatingFormula) -> DecisionLevel:
    return self.decision_level

  def backtrack(self: PropagatingFormula, d: DecisionLevel) -> None:
    self.decision_level = d
    self.formula.backtrack(d)
    while len(self.decision_history) > d:
      self.decision_history.pop()

  def get_assignment_object(self: PropagatingFormula) -> Assignment:
    return self.formula.get_assignment_object()