from __future__ import annotations
from typing import Dict, List, Tuple, TextIO, TYPE_CHECKING

if TYPE_CHECKING:
  Sign = int
  Variable = int
  Value = int
  Literal = Tuple[Sign, Variable]
  Clause = List[Literal]
  Formula = List[Clause]

def negate(lit: Literal):
  return (1 - lit[0], lit[1])

def max_1(lits: List[Literal]):
  cnf: Formula = []
  for i in range(len(lits)):
    for j in range(i + 1, len(lits)):
      cnf.append([negate(lits[i]), negate(lits[j])])
  return cnf

class BayesGraph:
  def __init__(self: BayesGraph, file_object: TextIO):
    graph_type = file_object.readline()
    if graph_type != "BAYES\n":
      raise Exception("File does not contain a Bayes network in .uai format")
    num_vars = file_object.readline()
    self.cardinalities = [ int(n) for n in file_object.readline().split() ]
    num_factors = int(file_object.readline())
    # handle factors in preamble
    self.factors: List[List[int]] = []
    for i in range(num_factors):
      factor_description = [ int(n) for n in file_object.readline().split() ]
      if factor_description[0] != len(factor_description) - 1:
        raise Exception("Number given for number of variables for factor does not match number of variables given for factor")
      self.factors.append(factor_description[1:])
    # handle function tables
    ft_description = file_object.read().split()
    self.tables: List[Dict[Tuple, str]] = []
    i = 0
    for factor_i in range(num_factors):
      table: Dict[Tuple, str] = {}
      num_entries = int(ft_description[i])
      i += 1
      assignment = [0 for i in self.factors[factor_i]]
      in_range = True
      while in_range:
        table[tuple(assignment)] = ft_description[i]
        i += 1
        in_range = False
        for j in range(len(assignment) -1, -1, -1):
          if assignment[j] < self.cardinalities[self.factors[factor_i][j]] - 1:
            assignment[j] += 1
            in_range = True
            break
          else:
            assignment[j] = 0
      self.tables.append(table)

  def to_formula(self: BayesGraph) -> Tuple[List[str], Formula]:
    cnf: Formula = []
    indicators: List[Tuple[int, int]] = [ (g_var, g_val) for g_var in range(len(self.cardinalities)) for g_val in range(self.cardinalities[g_var]) ]
    indicators_map = { indicators[i]: i for i in range(len(indicators)) }
    weights = [ '1.0' for _ in indicators ]
    # indicator exclusion constraints; a.k.a. variable assignment constraints
    for var in range(len(self.cardinalities)):
      cnf.extend(max_1([ (1, indicators_map[(var, val)]) for val in range(self.cardinalities[var]) ]))
    parameters = list((i, v, self.tables[i][v]) for i in range(len(self.factors)) for v in sorted(self.tables[i].keys()))
    weights.extend([ parameter[2] for parameter in parameters ])
    # print(parameters)
    parameters_map = { parameters[i]: i + len(indicators_map) for i in range(len(parameters)) }
    # parameter at-least-one constraints
    for i in range(len(self.factors)):
      params_in_factor = [ (i, assignment, self.tables[i][assignment]) for assignment in sorted(self.tables[i].keys()) ]
      cnf.append([ (1, parameters_map[param]) for param in params_in_factor ])
    # parameter implies assignment constraints
    for parameter in parameters:
      for var in range(len(parameter[1])):
        indicator = indicators_map[(self.factors[parameter[0]][var], parameter[1][var])]
        cnf.append([(0, parameters_map[parameter]), (1, indicator)])
    return weights, cnf

  def evidence_to_formula(self: BayesGraph, file_object: TextIO):
    evidence_description = [ int(i) for i in file_object.read().split()]
    if evidence_description[0] != (len(evidence_description) - 1) / 2:
      raise Exception("evidence file is improperly formatted")
    indicators_map = [0]
    for cardinality in self.cardinalities:
      indicators_map.append(indicators_map[-1] + cardinality)
    indicators_map.pop()
    cnf: Formula = []
    i = 0
    for i in range(1, len(evidence_description), 2):
      cnf.append([(1, indicators_map[evidence_description[i]] + evidence_description[i + 1])])
    return cnf

  def to_formula_file_with_evidence(self: BayesGraph, evidence: TextIO, ffile: TextIO, wfile: TextIO):
    weights, cnf = self.to_formula()
    cnf.extend(self.evidence_to_formula(evidence))
    ffile.write("p cnf {} {}\n".format(len(weights), len(cnf)))
    print(cnf)
    for clause in cnf:
      clause_str = " ".join([ ("" if sign else "-") + str(var) for sign, var in clause ]) + " 0\n"
      ffile.write(clause_str)
    wfile.write("p {}\n".format(len(weights)))
    for i in range(len(weights)):
      wfile.write("w {} {} 0\nw -{} 1.0 0\n".format(i, weights[i], i))