from __future__ import annotations
from typing import Dict, List, Optional, Set, TextIO, Tuple, TYPE_CHECKING, Union

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

  :param formula: A representation of the CNF
  :param base_state: maintains whether the formula, given the current assignment, is unresolved, satisfied, or unsatisfied
  :param variable_clauses: A map of variables to clauses that have them as their head or tail
  :param mutation_history: A list of what clauses have been mutated per each decision level
  :param unsat_clauses: A set of clauses that are unsatisfied given the current assignment
  :param state_history: A list of the state (i.e. unresolved, satisfied, or unsatisfied) of the formula at each decision level
  :param unit_clauses: A set of clauses that are unit given the current assignment
  :param decision_level: The current decision level
  :param assignment: An object maintaining the assignment of variables made at each decision level
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
    self.unsat_clauses: Set[Clause] = set()
    self.state_history: StateHistory = []
    self.unit_clauses: Set[Clause] = set()
    self.decision_level: DecisionLevel = 0
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
    """Add a clause to the formula, only during initialization.
    """
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
    """Add a clause to the formula after initialization.

    :param clause: a list of `Literal`s that are contained in the clause;
      each variable must appear in `clause` at most once. `clause` cannot contain literals
      in variables not already present in the representation.
    """
    clause_object = Clause(clause)
    clause_object.assign(self.assignment)
    self.formula.append(clause_object)

    # update mutation history and state history
    old_head_var, old_tail_var = clause_object.get_head_tail_var()
    was_valid = False
    was_unsat = len(clause) == 0
    for d in range(0, self.decision_level + 1):
      clause_object.assign_decision_level(self.assignment, d)
      state, head_var, tail_var = clause_object.get_state(self.assignment.get_assignment_at_level(d))
      if head_var != old_head_var or tail_var != old_tail_var:
        self.mutation_history[d].add(clause_object)

      # can actually be commented out since we never make
      # decisions while the formila is valid or unsat
      was_valid = was_valid or state == Clause.SATISFIED
      was_unsat = was_unsat or state == Clause.UNSATISFIED
      if self.state_history[d] == Formula.SATISFIED and not was_valid:
        self.state_history[d] = Formula.UNRESOLVED
      if was_unsat:
        self.state_history[d] = Formula.UNSATISFIED

    # update current state
    state, head_var, tail_var = clause_object.get_state(self.assignment)
    if state == Clause.UNRESOLVED or state == Clause.UNIT:
      if head_var not in self.variable_clauses:
        self.variable_clauses[head_var] = set()
      self.variable_clauses[head_var].add(clause_object)
      if tail_var not in self.variable_clauses:
        self.variable_clauses[tail_var] = set()
      self.variable_clauses[tail_var].add(clause_object)
    
    # update unit clauses
    if state == Clause.UNIT:
      self.unit_clauses.add(clause_object)

    # update unsat clauses
    if state == Clause.UNSATISFIED:
      self.unsat_clauses.add(clause_object)

  def assign(self: Formula, d: DecisionLevel, variable: Variable, value: Value, antecedent: Antecedent) -> None:
    """Record an assignment to the formula

    :param d: the decision level at which the assignment was made
    :param variable: the variable being assigned
    :param value: the value the variable is being assigned to
    :param antecedent: the antecedent that implied the assignment, if applicable
    """
    self.assignment.add_assignment(d, variable, value, antecedent)
    stale_clauses = self.variable_clauses.get(variable)
    state = self.state_history[-1]
    self.decision_level = d
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

        if clause_state == Clause.UNSATISFIED:
          self.unsat_clauses.add(clause)
        else:
          self.unsat_clauses.discard(clause)

    # persist formula state
    if d >= len(self.state_history):
      self.state_history.append(state)
    if not self.assignment.get_unassigned() and state == Formula.UNRESOLVED:
      self.state_history[-1] = Formula.SATISFIED
    else:
      self.state_history[-1] = state

  def backtrack(self: Formula, d: DecisionLevel) -> None:
    """Backtrack to a previous decision level

    :param d: a decision level smaller than the current decision level
    """
    self.decision_level = d
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
        if clause_state == Clause.UNSATISFIED:
          self.unsat_clauses.add(clause)
        else:
          self.unsat_clauses.discard(clause)

  def get_current_state(self: Formula) -> State:
    if self.base_state == Formula.UNSATISFIED:
      return Formula.UNSATISFIED
    return self.state_history[-1]

  def get_partial_assignment(self: Formula) -> Assignment:
    return self.assignment

  def get_unit_clauses(self: Formula) -> Set[Clause]:
    return self.unit_clauses

  def get_unsat_clauses(self: Formula) -> Set[Clause]:
    return self.unsat_clauses

  def get_decision_level(self: Formula) -> DecisionLevel:
    return self.decision_level