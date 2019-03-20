from typing import Any, Dict, List, Optional, Set, TextIO, Tuple, Union
import sys
import math

TRUE = 1
UNDEFINED = 0.5
FALSE = 0

# Note limitation in Python: Set-like structures cannot serve as keys
# in other structures
Literal = int
Clause = Set[Literal]
ClauseRef = int
Formula = Dict[ClauseRef, Clause]
VariablesIndex = Dict[Literal, Tuple[Set[ClauseRef], Set[ClauseRef]]]
SizeIndex = Dict[int, Set[ClauseRef]]
IndexedFormula = Tuple[Formula, VariablesIndex, SizeIndex]
Problem = Tuple[IndexedFormula, int, int]

Variable = int
Value = Union[int, float]
Assignment = Dict[Variable, Value]

## Debugging functions
def assert_well_formed(ind_formula: IndexedFormula) -> None:
  if is_empty_formula(ind_formula):
    raise Exception("Formula is empty")
  if has_empty_clause(ind_formula):
    raise Exception("Formula has empty clause")
  formula, vars_ind, size_ind = ind_formula
  if not vars_ind:
    raise Exception("vars_ind is empty")
  if not size_ind:
    raise Exception("size_ind is empty")
  for var, lits in vars_ind.items():
    if not lits[0] | lits[1]:
      raise Exception(str(var) + " in vars_index has both empty neg_lits and empty pos_lits")
    if lits[0] & lits[1]:
      raise Exception(str(var) + " in vars_index has clauses " + str(lits[0] & lits[1]) + " in both neg_lits and pos_lits")
    for i in range(2):
      for clause_ref in lits[i]:
        if clause_ref not in formula:
          raise Exception(str(clause_ref) + " is in variable " + str(var) + " of vars_index but not in formula")
        if var * (i * 2 - 1) not in formula[clause_ref]:
          raise Exception(str(clause_ref) + " is in variable " + str(var) + " of vars_index but literal " + str(var * (i * 2 - 1)) + " is not in " + str(formula[clause_ref]))
  for n, refs in size_ind.items():
    if not refs:
      raise Exception(str(var) + " in size_index has empty set of clauses")
    for clause_ref in refs:
      if clause_ref not in formula:
        raise Exception(str(clause_ref) + " is in size " + str(n) + " of size_index but not in formula")
      if n != len(formula[clause_ref]):
        raise Exception(str(clause_ref) + " is in size " + str(n) + " of size_index but has size " + str(len(formula[clause_ref])))

## Utility functions

def assign(ind_formula: IndexedFormula, variable: Variable, value: Value) -> Union[bool, IndexedFormula]:
  formula, vars_ind, size_ind = ind_formula
  if variable not in vars_ind or isinstance(value, float):
    return ind_formula

  # remove clauses that are satisfied by assignment
  for clause_ref in vars_ind[variable][value]:
    clause = formula[clause_ref]

    # remove clause from formula
    del formula[clause_ref]

    # remove clause from variable index
    for l in clause:
      if abs(l) == variable:
        continue
      var_lits = vars_ind[abs(l)]
      var_lits[FALSE if l < 0 else TRUE].remove(clause_ref)
      if not var_lits[0] and not var_lits[1]:
        del vars_ind[abs(l)]

    # remove clause from size index
    size_ind[len(clause)].remove(clause_ref)
    if not size_ind[len(clause)]:
      del size_ind[len(clause)]

  # return if formula is empty
  if not formula:
    return True

  # remove literals containing variable from variables that cannot be satisfied by assignment
  for clause_ref in vars_ind[variable][1 - value]:
    clause = formula[clause_ref]
    clause.remove(variable * (-2 * value + 1))
    clause_size = len(clause)
    # return if formula has empty clause
    if clause_size == 0:
      return False
    size_ind[clause_size + 1].remove(clause_ref)
    if not size_ind[clause_size + 1]:
      del size_ind[clause_size + 1]
    if clause_size not in size_ind:
      size_ind[clause_size] = set()
    size_ind[clause_size].add(clause_ref)

  del vars_ind[variable]
  assert_well_formed(ind_formula)
  return ind_formula

def add_clause(clause: Clause, ind_formula: IndexedFormula) -> None:
  formula, vars_ind, size_ind = ind_formula
  clause_ref = id(clause)
  formula[clause_ref] = clause

  # update variables index
  for l in clause:
    v = abs(l)
    if v not in vars_ind:
      vars_ind[v] = (set(), set())
    if l < 0: # if literal is a negated variable
      vars_ind[v][0].add(clause_ref)
    else:
      vars_ind[v][1].add(clause_ref)

  # update size index
  clause_size = len(clause)
  if clause_size not in size_ind:
    size_ind[clause_size] = set()
  size_ind[clause_size].add(clause_ref)

def clone_ind_formula(ind_formula: IndexedFormula) -> IndexedFormula:
  new_ind_formula: IndexedFormula = ({}, {}, {})
  formula, _, _ = ind_formula
  for clause in formula.values():
    add_clause({ l for l in clause }, new_ind_formula)
  return new_ind_formula

## I/O Functions

def parse_cnf(file_object: TextIO) -> Problem:
  # Note about parsing: see https://people.sc.fsu.edu/~jburkardt/data/cnf/cnf.html
  # assumption: no (x or -x) in each clause; i.e. no clause is tautological
  def check_taut_clause(clause: Clause) -> None:
    for l in clause:
      if -l in clause:
        raise Exception("Error! Clause is tautological!")

  ind_formula: IndexedFormula = ({}, {}, {})
  current_clause: Clause = set()
  num_vars: Optional[int] = None
  num_clauses: Optional[int] = None

  for line in file_object:
    # Note: each line has at least a single character
    if line[0] == 'c':
      continue
    if line[0] == 'p':
      if num_vars or num_clauses:
        raise Exception("Error! Input file has multiple problem lines")
      num_vars, num_clauses = [ int(n) for n in line.split()[2:] ]
      continue
    literals = [ int(l) for l in line.split() ]
    for l in literals:
      # handle clause separator; some examples have clauses
      # that span several lines
      if l == 0:
        check_taut_clause(current_clause)
        add_clause(current_clause, ind_formula)
        current_clause = set()
        continue
      # append each literal to the current clause
      current_clause.add(l)
  # some examples do not terminate the final clause with 0
  if current_clause:
    check_taut_clause(current_clause)
    add_clause(current_clause, ind_formula)
  # validate file
  if num_clauses is None or num_vars is None:
    raise Exception("p line not specified")
  if len(ind_formula[0]) != num_clauses:
    raise Exception("Number of clauses do not match given number in problem description")
  if len(ind_formula[1]) != num_vars:
    raise Exception("Number of variables do not match given number in problem description")
  return ind_formula, num_vars, num_clauses

# tactics

def is_empty_formula(ind_formula: IndexedFormula) -> bool:
  return not ind_formula[0]

def has_empty_clause(ind_formula: IndexedFormula) -> bool:
  for clause in ind_formula[0].values():
    if not clause:
      return True
  return False

def choose_arbitrary_branching_variable(ind_formula: IndexedFormula) -> Variable:
  _, vars_ind, _ = ind_formula
  return next(iter(vars_ind))

def unit_propagate(ind_formula: Union[bool, IndexedFormula]) -> Union[bool, IndexedFormula]:
  if isinstance(ind_formula, bool):
    return ind_formula
  formula, vars_ind, size_ind = ind_formula
  assert_well_formed(ind_formula)
  while True:

    # pure variable propagation
    pure_vars = set()
    for k in vars_ind:
      if not vars_ind[k][0] or not vars_ind[k][1]:
        pure_vars.add(k)
    for var in pure_vars:
      if var not in vars_ind:
        continue
      ind_formula = assign(ind_formula, var, FALSE if vars_ind[var][0] else TRUE)
      if isinstance(ind_formula, bool):
        return ind_formula
      formula, vars_ind, size_ind = ind_formula

    # unit elimination
    if size_ind.get(1):
      assert_well_formed(ind_formula)
      clause_ref = next(iter(size_ind[1]))
      l = next(iter(formula[clause_ref]))
      ind_formula = assign(ind_formula, abs(l), FALSE if l < 0 else TRUE)
      if isinstance(ind_formula, bool):
        return ind_formula
      formula, vars_ind, size_ind = ind_formula
    else:
      break
  return ind_formula

def dpll(ind_formula: Union[bool, IndexedFormula], depth: int) -> bool:
  """
  Assumption: ind_formula is True or is False or is a formula that is
  neither empty nor contains an empty clause
  """
  if isinstance(ind_formula, bool):
    return ind_formula
  ind_formula = unit_propagate(ind_formula)
  if isinstance(ind_formula, bool):
    return ind_formula
  var = choose_arbitrary_branching_variable(ind_formula)
  if dpll(assign(clone_ind_formula(ind_formula), var, FALSE), depth + 1):
    return True
  else:
    return dpll(assign(ind_formula, var, TRUE), depth + 1)

def main() -> None:
  infilename = sys.argv[1]
  with open(infilename) as infile:
    problem = parse_cnf(infile)
    ind_formula = problem[0]
    if is_empty_formula(ind_formula):
      print(True)
    elif has_empty_clause(ind_formula):
      print(False)
    else:
      print(dpll(ind_formula, 0))

if __name__ == "__main__":
  main()
