from __future__ import annotations
from typing import Dict, List, Optional, Set, TextIO, TYPE_CHECKING, Union

from clause import Clause
from assignment import Assignment

if TYPE_CHECKING:
  from shared_types import DecisionLevel, Literal, Value, Variable
  from assignment import Antecedent

  VariableClauses = Dict[Variable, Set[Clause]]
  State = Union[int, float]

  MutationHistory = List[Set[Clause]]
  StateHistory = List[State]

class Formula:
  """

  The `Formula` class is used to represent a CNF formula and a partial
  assignment on it at various decision levels. Under a legal
  construction of a Formula object and invocation of mutation methods,
  a `Formula` object should always be in a consistent state in the
  following sense:

  either `self.base_state` is not `UNRESOLVED`, or `self.state` reflects
  whether the partial assignment on it satisfies all clauses of the
  formula (`SATISFIED`), leaves some clause unsatisfiable
  (`UNSATISFIED`), or for each clause, a superset of the current
  assignment satisfies it, but not all clauses are satisfied by the
  current assignment (`UNRESOLVED`); moreover, calling `backtrack` with
  some decision level `d` removes the partial assignments made at a
  decision level greater than `d`.

  Calling a mutation method when `self.base_state` is not `UNRESOLVED`
  gives undefined behavior.
  """

  SATISFIED: State = 1
  UNRESOLVED: State = 0.5
  UNSATISFIED: State = 0

  def __init__(self: Formula, file_object: TextIO) -> None:
    """Construct a Formula object from a TextIO object whose contents specify a CNF

    In the input format, clauses may be of a generalized form that
    may be empty or contain repeated literals (untested). In the representation,
    they are normalized to a CNF; that is, with empty clauses and
    tautological clauses omitted, and among those clauses that are
    represented, repeated literals are condensed into a single one.

    It is separately maintained in `self.base_state` whether the
    representation is an empty formula or contains an empty clause.
    If either are true, then we allow that the representation may
    not share the same satisfiability as the input CNF.
    """
    self.formula: List[Clause] = []
    self.base_state: State = Formula.UNRESOLVED
    # `variable_clauses` is a map from variables to clauses that have
    # points to a literal in that variable in its head reference or
    # tail reference per decision level
    self.variable_clauses: VariableClauses = {}
    self.mutation_history: MutationHistory = [set()]
    self.state_history: StateHistory = []
    self.unit_clauses: Set[Clause] = set()
    variables_in_representation: Set[Variable] = set()

    num_vars: Optional[int] = None
    num_clauses: Optional[int] = None
    current_clause: Set[Literal] = set()
    current_clause_valid = False
    num_ignored_clauses = 0
    variables: Set[Variable] = set()

    for line in file_object:
      if line[0] == 'c':
        continue
      if line[0] == 'p':
        if num_vars or num_clauses:
          raise Exception("Error! Input file has multiple problem lines")
        num_vars, num_clauses = [ int(n) for n in line.split()[2:] ]
        continue
      literals = [ int(l) for l in line.split() ]
      for l in literals:
        if l == 0:
          # handle empty clauses
          if not current_clause:
            self.base_state = Formula.UNSATISFIED
            num_ignored_clauses += 1
          # handle tautological clauses
          if not current_clause_valid:
            # non-empty, non-tautological clauses added to representation
            variables_in_representation |= { abs(l) for l in current_clause }
            self._add_base_clause(sorted(list(current_clause)))

          # reset for next clause
          current_clause = set()
          current_clause_valid = False
          continue

        # Tautological clauses are not added
        if -l in current_clause and not current_clause_valid:
          current_clause_valid = True
          num_ignored_clauses += 1

        current_clause.add(l)
        variables.add(abs(l))

    # some examples do not terminate the final clause with 0
    if current_clause:
      # handle tautological clauses
      if current_clause_valid:
        num_ignored_clauses += 1
      # handle non-empty, non-tautological clauses
      else:
        variables_in_representation |= { abs(l) for l in current_clause }
        self._add_base_clause(sorted(list(current_clause)))
    if num_clauses is None or num_vars is None:
      raise Exception("p line not specified")
    if len(self.formula) + num_ignored_clauses != num_clauses:
      raise Exception("Number of clauses do not match given number in problem description")
    if len(variables) != num_vars:
      raise Exception("Number of variables do not match given number in problem description")

    # handle empty formulas
    if len(self.formula) == 0:
      self.base_state = Formula.SATISFIED

    self.state_history.append(self.base_state)
    self.assignment: Assignment = Assignment(variables_in_representation)

  def _add_base_clause(self: Formula, clause: List[int]) -> None:
    clause_object = Clause(clause)
    self.formula.append(clause_object)
    head_var, tail_var = clause_object.get_head_tail_var()
    if head_var not in self.variable_clauses:
      self.variable_clauses[head_var] = set()
    self.variable_clauses[head_var].add(clause_object)
    if tail_var not in self.variable_clauses:
      self.variable_clauses[tail_var] = set()
    self.variable_clauses[tail_var].add(clause_object)
    if len(clause) == 1:
      self.unit_clauses.add(clause_object)

  def add_clause(self: Formula, clause: List[int]) -> None:
    """

    :param clause: a list of `Literal`s that are contained in the clause;
      each variable must appear in `clause` at most once. `clause` cannot contain literals
      in variables not already present in the representation.
    :param assignment: the current assignment that the clause should be
      aware of
    """
    clause_object = Clause(clause)
    clause_object.assign(self.assignment)
    self.formula.append(clause_object)
    state, head_var, tail_var = clause_object.get_state(self.assignment)
    if state == Clause.UNRESOLVED or state == Clause.UNIT:
      if head_var not in self.variable_clauses:
        self.variable_clauses[head_var] = set()
      self.variable_clauses[head_var].add(clause_object)
      if tail_var not in self.variable_clauses:
        self.variable_clauses[tail_var] = set()
      self.variable_clauses[tail_var].add(clause_object)
    if state == Clause.UNIT:
      self.unit_clauses.add(clause_object)

  def assign(self: Formula, d: DecisionLevel, variable: Variable, value: Value, antecedent: Antecedent) -> None:
    self.assignment.add_assignment(d, variable, value, antecedent)
    stale_clauses = self.variable_clauses.get(variable)
    state = self.state_history[-1]
    if stale_clauses:
      # update variable_clauses state (1/2)
      del self.variable_clauses[variable]
      for clause in stale_clauses:
        # update clause state
        clause.assign(self.assignment)

        # update variable_clauses state (2/2)
        clause_state, head_var, tail_var = clause.get_state(self.assignment)
        if clause_state == Clause.UNRESOLVED or clause_state == Clause.UNIT:
          if head_var not in self.variable_clauses:
            self.variable_clauses[head_var] = set()
          self.variable_clauses[head_var].add(clause)
          if tail_var not in self.variable_clauses:
            self.variable_clauses[tail_var] = set()
          self.variable_clauses[tail_var].add(clause)

        # update formula state
        if clause_state == Clause.UNSATISFIED:
          state = Formula.UNSATISFIED

        # update mutation history
        while d >= len(self.mutation_history):
          self.mutation_history.append(set())
        self.mutation_history[-1].add(clause)

        # update unit_clauses
        if clause_state == Clause.UNIT:
          self.unit_clauses.add(clause)
        else:
          self.unit_clauses.discard(clause)

    # persist formula state
    if d >= len(self.state_history):
      self.state_history.append(state)
    if not self.assignment.get_unassigned() and state == Formula.UNRESOLVED:
      self.state_history[-1] = Formula.SATISFIED
    else:
      self.state_history[-1] = state

  def backtrack(self: Formula, d: DecisionLevel) -> None:
    while len(self.state_history) > d + 1:
      self.state_history.pop()
    self.assignment.backtrack(d)
    while len(self.mutation_history) > d + 1:
      clauses = self.mutation_history.pop()
      for clause in clauses:
        old_head_var, old_tail_var = clause.get_head_tail_var()
        self.variable_clauses.get(old_head_var, set()).discard(clause)
        self.variable_clauses.get(old_tail_var, set()).discard(clause)
        clause.backtrack(d)
        clause_state, head_var, tail_var = clause.get_state(self.assignment)
        if clause_state == Clause.UNRESOLVED or clause_state == Clause.UNIT:
          if head_var not in self.variable_clauses:
            self.variable_clauses[head_var] = set()
          self.variable_clauses[head_var].add(clause)
        if clause_state == Clause.UNRESOLVED:
          if tail_var not in self.variable_clauses:
            self.variable_clauses[tail_var] = set()
          self.variable_clauses[tail_var].add(clause)
        if clause_state == Clause.UNIT:
          self.unit_clauses.add(clause)
        else:
          self.unit_clauses.discard(clause)

  def get_current_state(self: Formula) -> State:
    if self.base_state == Formula.UNSATISFIED:
      return Formula.UNSATISFIED
    return self.state_history[-1]

  def get_assignment_object(self: Formula) -> Assignment:
    return self.assignment
