from __future__ import annotations
from typing import TextIO,  TYPE_CHECKING

from propagating_formula import PropagatingFormula
from arbitrary_brancher import ArbitraryBrancher
from fuip_analyzer import fuip_analyzer

if TYPE_CHECKING:
  from shared_types import ConflictAnalyzer
  from propagating_formula import State

UNSATISFIED: State = PropagatingFormula.UNSATISFIED
SATISFIABLE: State = PropagatingFormula.SATISFIED

def cdcl(file_object: TextIO) -> State:
  formula = PropagatingFormula(file_object)
  brancher = ArbitraryBrancher.create(formula)
  conflict_analyzer = fuip_analyzer

  if formula.get_current_state() == PropagatingFormula.UNSATISFIED:
    return UNSATISFIED
  while formula.get_current_state() != PropagatingFormula.SATISFIED:
    variable, value = brancher.make_decision(formula.get_partial_assignment())
    formula.assign(variable, value)
    while formula.get_current_state() == PropagatingFormula.UNSATISFIED:
      if formula.get_decision_level() == 0:
        return UNSATISFIED
      new_decision_level, new_clauses = conflict_analyzer(formula)
      if new_decision_level < 0:
        return UNSATISFIED
      formula.backtrack(new_decision_level)
      for clause in new_clauses:
        formula.add_clause(clause)
  return SATISFIABLE