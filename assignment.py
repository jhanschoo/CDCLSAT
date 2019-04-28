from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
  from shared_types import DecisionLevel, Variable, Value
  from clause import Clause

  Antecedent = Optional[Clause]
  AssignmentItem = Tuple[DecisionLevel, Variable, Value, Antecedent]

class Assignment:

  def __init__(self: Assignment, variables: Set[Variable]) -> None:
    self.history: List[Dict[Variable, AssignmentItem]] = []
    self.current: Dict[Variable, AssignmentItem] = {}
    self.unassigned_variables = variables
    pass

  def __contains__(self: Assignment, key: Variable) -> bool:
    return key in self.current

  def __len__(self: Assignment) -> int:
    return len(self.current)

  def add_assignment(self: Assignment, d: DecisionLevel, variable: Variable, value: Value, antecedent: Antecedent) -> None:
    self.unassigned_variables.remove(variable)
    item = (d, variable, value, antecedent)
    self.current[variable] = item
    while len(self.history) <= d:
      self.history.append({})
    self.history[d][variable] = item

  def backtrack(self: Assignment, d: DecisionLevel) -> None:
    while len(self.history) > d + 1:
      d_assignments = self.history.pop()
      for variable in d_assignments:
        del self.current[variable]
        self.unassigned_variables.add(variable)

  def get_value(self: Assignment, variable: Variable) -> Value:
    if variable in self.current:
      return self.current[variable][2]
    return 0.5

  def get_decision_level(self: Assignment, variable: Variable) -> Optional[DecisionLevel]:
    if variable in self.current:
      return self.current[variable][0]
    return None

  def get_antecedent(self: Assignment, variable: Variable) -> Antecedent:
    if variable in self.current:
      return self.current[variable][3]
    return None

  def get(self: Assignment, variable: Variable) -> Optional[AssignmentItem]:
    if variable in self.current:
      return self.current[variable]
    return None

  def get_unassigned(self: Assignment) -> Set[Variable]:
    return self.unassigned_variables
  
  def get_assignment_at_level(self: Assignment, d: DecisionLevel) -> Dict[Variable, AssignmentItem]:
    return self.history[d]