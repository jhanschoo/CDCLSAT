from __future__ import annotations
from typing import Dict, List, Optional, Tuple, TextIO, TYPE_CHECKING

if TYPE_CHECKING:
  # Type of the sign of a logical literal
  Sign = int
  # Type of a logical variable
  Variable = int
  # Type of a logical value
  Value = int
  # Type of a logical literal
  Literal = Tuple[Sign, Variable]
  # Type of a CNF clause, a list of literals
  Clause = List[Literal]
  # Type of a CNF formula, a list of clauses
  Formula = List[Clause]

def negate(lit: Literal):
  """Negates a logical literal
  :param lit: a logical literal
  :returns: the negation of the literal lit
  """
  return (1 - lit[0], lit[1])

def max_1(lits: List[Literal]):
  """Generates a CNF that is satisfied exactly when at most one literal in the list is satisfied
  :param lits: a list of literals
  :returns: a CNF that is satisfied exactly when at most one literal in the list is satisfied
  """
  cnf: Formula = []
  for i in range(len(lits)):
    for j in range(i + 1, len(lits)):
      cnf.append([negate(lits[i]), negate(lits[j])])
  return cnf

class BayesGraph:
  """Representation of a Bayes Net, with functions to convert the representation to a CNF encoding of it

  :param cardinalities: a list of integers, where the integer at index i is the cardinality of the random variable i of the graph
  :param factors: a list of vertices of the graph in the following representation: each vertex is a list of integers where the last integer represents the random variable that the vertex corresponds to, and the other integers in the list represent the random variables of the parents of this vertex; that is, the only other random variables in the graph that this vertex's random variable is conditionally dependent on, given the graph; we say that these random variables are local to this vertex.
  :param tables: a list of maps. The map at each index corresponds to the vertex at the same index of the `factors` attribute. Each map maps from an assignment of the local random variables of the vertex, to the local (conditional) probability of that assignment, which is represented as a string to avoid premature loss of precision
  """

  def __init__(self: BayesGraph, file_object: TextIO):
    """Initialize a BayesGraph object from an input file in .uai format
    """
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
    # for each factor
    for factor_i in range(num_factors):
      table: Dict[Tuple, str] = {}
      num_entries = int(ft_description[i])
      i += 1
      # iterate through each assignment to local random variables
      assignment = [0 for i in self.factors[factor_i]]
      in_range = True
      while in_range:
        # and record that assignment with its probability in the map
        table[tuple(assignment)] = ft_description[i]
        i += 1
        # then update the assignment to the next iterand
        in_range = False
        for j in range(len(assignment) -1, -1, -1):
          if assignment[j] < self.cardinalities[self.factors[factor_i][j]] - 1:
            assignment[j] += 1
            in_range = True
            break
          else:
            assignment[j] = 0
      self.tables.append(table)

    self._memo_to_formula: Optional[Tuple[List[str], Formula]] = None

  def to_formula(self: BayesGraph) -> Tuple[List[str], Formula]:
    """Maps the graph represented by this object to a CNF encoding thereof, with weights
    :returns: A tuple containing the weights, followed the CNF. The weights are a list of strings representing floats, where the float at index i is the weight-contribution of the literal of the unnegated logical variable i to the models that satisfy that literal. We omit the weights-contributions of negative literals since they all contribute the multiplicative identity (i.e. 1.0) in our representation. The CNF is a list of clauses, where each clause is a list of literals, where each literal is a tuple of two elements; the zeroth is a sign in either a 0 or 1; with 0 representing a negative literal and 1 a positive literal; the first is an integer representing the variable of the literal.
    """
    if self._memo_to_formula is not None:
      return self._memo_to_formula
    cnf: Formula = []
    # a list of the indicator random variables for the CNF. An indicator random variable is created for each assignment of a random variable to one of its values, for each random variable in the graph.
    indicators: List[Tuple[int, int]] = [ (g_var, g_val) for g_var in range(len(self.cardinalities)) for g_val in range(self.cardinalities[g_var]) ]
    # a reverse map of the indicators list
    indicators_map = { indicators[i]: i for i in range(len(indicators)) }
    # we initialize the weights with the weights of the indicator variables, which all have multiplicative identity.
    weights = [ '1.0' for _ in indicators ]
    # indicator exclusion constraints; a.k.a. variable assignment constraints
    for var in range(len(self.cardinalities)):
      cnf.extend(max_1([ (1, indicators_map[(var, val)]) for val in range(self.cardinalities[var]) ]))
    # a list of parameter variables. A parameter variable is created for each entry in the function table of a vertex, for each vertex of the graph.
    parameters = list((i, v, self.tables[i][v]) for i in range(len(self.factors)) for v in sorted(self.tables[i].keys()))
    # a reverse map of the parameters list
    parameters_map = { parameters[i]: i + len(indicators_map) for i in range(len(parameters)) }
    # we append the parameter variables' weights; which are exactly the local probabilities in the respective function table entries corresponding to the parameters.
    weights.extend([ parameter[2] for parameter in parameters ])
    # parameter at-least-one constraints
    for i in range(len(self.factors)):
      params_in_factor = [ (i, assignment, self.tables[i][assignment]) for assignment in sorted(self.tables[i].keys()) ]
      cnf.append([ (1, parameters_map[param]) for param in params_in_factor ])
    # parameter implies assignment constraints
    for parameter in parameters:
      for var in range(len(parameter[1])):
        indicator = indicators_map[(self.factors[parameter[0]][var], parameter[1][var])]
        cnf.append([(0, parameters_map[parameter]), (1, indicator)])
    self._memo_to_formula = (weights, cnf)
    return weights, cnf

  def evidence_to_formula(self: BayesGraph, file_object: TextIO):
    """Creates a CNF representing evidence (i.e. observed vertices and their values) on the graph from a .uai.evid file representation. Note that in our representation, the indicator variable that the random variable i is set to its jth value is the nth indicator variable where n is the sum of the cardinalities of all the random variables before i, then added to j.
    :returns: a CNF representing evidence
    """
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
    """Write a CNF encoding of the graph represented by this object to a file in DIMACS format, together with an associated weights file.
    """
    weights, cnf = self.to_formula()
    cnf.extend(self.evidence_to_formula(evidence))
    ffile.write("p cnf {} {}\n".format(len(weights), len(cnf)))
    for clause in cnf:
      clause_str = " ".join([ ("" if sign else "-") + str(var) for sign, var in clause ]) + " 0\n"
      ffile.write(clause_str)
    wfile.write("p {}\n".format(len(weights)))
    for i in range(len(weights)):
      wfile.write("w {} {} 0\nw -{} 1.0 0\n".format(i, weights[i], i))
