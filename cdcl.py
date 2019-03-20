from __future__ import annotations
from typing import TextIO,  TYPE_CHECKING

from propagating_formula import PropagatingFormula
from arbitrary_brancher import ArbitraryBrancher

if TYPE_CHECKING:
  from shared_types import ConflictAnalyzer
  from propagating_formula import State

UNSATISFIED: State = PropagatingFormula.UNSATISFIED
SATISFIABLE: State = PropagatingFormula.SATISFIED

def CDCL(file_object: TextIO) -> State:
  formula = PropagatingFormula(file_object)
  brancher = ArbitraryBrancher.create(formula)
  conflict_analyzer = FUIPAnalyzer()

  if formula.get_current_state() == PropagatingFormula.UNSATISFIED:
    return UNSATISFIED
  while formula.get_current_state() != PropagatingFormula.SATISFIED:
    variable, value = brancher.make_decision(formula.get_assignment_object())
    formula.assign(variable, value)
    while formula.get_current_state() == PropagatingFormula.UNSATISFIED:
      new_decision_level, new_clauses = conflict_analyzer(formula)
      if new_decision_level < 0:
        return UNSATISFIED
      formula.backtrack(new_decision_level) # TODO: how to remember bad decisions?
      for clause in new_clauses:
        formula.add_clause(clause)
  return SATISFIABLE