from __future__ import annotations
from typing import Tuple, TextIO, TYPE_CHECKING

from propagating_formula import PropagatingFormula
from vsids_brancher import VSIDSBrancher
from random_brancher import RandomBrancher
from two_choice_brancher import TwoChoiceBrancher
from fuip_analyzer import fuip_analyzer

if TYPE_CHECKING:
  from shared_types import ConflictAnalyzer
  from propagating_formula import State

UNSATISFIED: State = PropagatingFormula.UNSATISFIED
SATISFIABLE: State = PropagatingFormula.SATISFIED

def cdcl(file_object: TextIO) -> Tuple[State, int]:
  formula = PropagatingFormula(file_object)
  brancher = RandomBrancher.create(formula)
  conflict_analyzer = fuip_analyzer

  if formula.get_current_state() == PropagatingFormula.UNSATISFIED:
    return UNSATISFIED, brancher.decision_count
  while formula.get_current_state() != PropagatingFormula.SATISFIED:
    variable, value = brancher.make_decision(formula.get_partial_assignment())
    formula.assign(variable, value)
    while formula.get_current_state() == PropagatingFormula.UNSATISFIED:
      if formula.get_decision_level() == 0:
        return UNSATISFIED, brancher.decision_count
      new_decision_level, new_clauses = conflict_analyzer(formula, brancher)
      if new_decision_level < 0:
        return UNSATISFIED, brancher.decision_count
      formula.backtrack(new_decision_level)
      for clause in new_clauses:
        brancher.record_learned_clause(clause)
        formula.add_clause(clause)
  return SATISFIABLE, brancher.decision_count