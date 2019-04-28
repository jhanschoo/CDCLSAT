from __future__ import annotations
from typing import Dict, List, Tuple, TYPE_CHECKING, Union

if TYPE_CHECKING:
  from shared_types import DecisionLevel, Literal, Value, Variable
  from assignment import AssignmentItem, Assignment

  HeadReference = int
  TailReference = int
  State = Union[int, float]

def z2no(v: Value) -> int:
  """
  Transforms values in { False = 0, undefined = 0.5, True = 1 } to
  values in { False = -1, undefined = 0, True = 1 }; function name is
  "zero to negative one"
  """
  return int(v * 2 - 1)

class Clause:
  SATISFIED: State = 1
  UNSATISFIED: State = 0
  UNRESOLVED: State = 0.5
  UNIT: State = -0.5

  def __init__(self, clause: List[Literal]) -> None:
    """Construct a `Clause` object from a list specification of its literals

    :param clause: After construction,
      it is prohibited to modify `clause` outside of code in `Clause`
    """
    if len(clause) == 0:
      raise Exception("input {} to Clause constructor is empty list".format(clause))
    self.clause: List[Literal] = clause
    self.reference_history: List[Tuple[DecisionLevel, HeadReference, TailReference]] = [(0, 0, len(clause) - 1)]

  def _update_history(self: Clause, d: DecisionLevel, head: HeadReference, tail: TailReference) -> None:
    max_seen_reference_history = self.reference_history[-1][0]
    if d <= max_seen_reference_history:
      # note that we set the decision level associated with this state
      # of head and tail pointers to the maximum of those seen so far
      # otherwise backtracking will terminate prematurely
      self.reference_history[-1] = (max_seen_reference_history, head, tail)
    else:
      self.reference_history.append((d, head, tail))

  def assign_decision_level(self: Clause, assignment: Assignment, d: DecisionLevel) -> None:
    self.assign(assignment.get_assignment_at_level(d))

  def assign(self: Clause, assignment: Union[Dict[Variable, AssignmentItem], Assignment]) -> None:
    """Update the clause with a more specific assignment at a not lower decision level

    :param nu: An assignment of variables to values that is a
      superset of the assignments previously passed into previous
      `assign` invocations except for those assignments that have since
      been `backtrack`ed
    """
    # TODO: Return all variables at the current decision level
    head, tail = self.reference_history[-1][1:]

    head_lit = self.clause[head]
    head_item = assignment.get(abs(head_lit))
    while head < tail and head_item and head_lit * z2no(head_item[2]) == -abs(head_lit):
      head_decision_level = head_item[0]
      head += 1
      self._update_history(head_decision_level, head, tail)
      head_lit = self.clause[head]
      head_item = assignment.get(abs(head_lit))

    tail_lit = self.clause[tail]
    tail_item = assignment.get(abs(tail_lit))
    while head < tail and tail_item and tail_lit * z2no(tail_item[2]) == -abs(tail_lit):
      tail_decision_level = tail_item[0]
      tail -= 1
      self._update_history(tail_decision_level, head, tail)
      tail_lit = self.clause[tail]
      tail_item = assignment.get(abs(tail_lit))

  def backtrack(self: Clause, d: DecisionLevel):
    """Backtrack the clause's assignments to a lower, nonnegative decision level `d`
    """
    while self.reference_history[-1][0] > d:
      self.reference_history.pop()

  def get_state(self: Clause, assignment: Union[Dict[Variable, AssignmentItem], Assignment]) -> Tuple[State, Variable, Variable]:
    head, tail = self.reference_history[-1][1:]
    head_lit = self.clause[head]
    tail_lit = self.clause[tail]
    head_var = abs(head_lit)
    tail_var = abs(tail_lit)
    head_item = assignment.get(head_var)
    tail_item = assignment.get(tail_var)
    if (head_item and head_lit * z2no(head_item[2]) == head_var) \
      or (tail_item and tail_lit * z2no(tail_item[2]) == tail_var):
      return (Clause.SATISFIED, head_var, tail_var)
    if head_item and head_lit * z2no(head_item[2]) == -head_var \
      and head == tail:
      return (Clause.UNSATISFIED, head_var, tail_var)
    if head == tail:
      return (Clause.UNIT, head_var, tail_var)
    return (Clause.UNRESOLVED, head_var, tail_var)

  def get_head_tail_var(self: Clause) -> Tuple[Variable, Variable]:
    head, tail = self.reference_history[-1][1:]
    return (abs(self.clause[head]), abs(self.clause[tail]))

  def get_head_tail_lit(self: Clause) -> Tuple[Literal, Literal]:
    head, tail = self.reference_history[-1][1:]
    return (self.clause[head], self.clause[tail])

  def get_assigned_vars(self: Clause, assignment: Assignment) -> List[Variable]:
    vars = []
    for l in self.clause:
      if abs(l) in assignment:
        vars.append(abs(l))
    return vars