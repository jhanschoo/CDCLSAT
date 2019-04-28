import sys

from bayes_graph import BayesGraph

toy_A = {
  (0,): 0.4,
  (1,): 0.6
}

toy_B = {
  (0, 0): 0.1,
  (0, 1): 0.2,
  (0, 2): 0.7,
  (1, 0): 0.2,
  (1, 1): 0.3,
  (1, 2): 0.5
}

toy_C = {
  (0, 0, 0): 0.1,
  (0, 0, 1): 0.9,
  (0, 1, 0): 0.2,
  (0, 1, 1): 0.8,
  (0, 2, 0): 0.3,
  (0, 2, 1): 0.7,
  (1, 0, 0): 0.4,
  (1, 0, 1): 0.6,
  (1, 1, 0): 0.6,
  (1, 1, 1): 0.4,
  (1, 2, 0): 0.7,
  (1, 2, 1): 0.3
}

toy_D = {
  (0, 0, 0): 0.9,
  (0, 0, 1): 0.1,
  (0, 1, 0): 0.8,
  (0, 1, 1): 0.2,
  (0, 2, 0): 0.7,
  (0, 2, 1): 0.3,
  (1, 0, 0): 0.4,
  (1, 0, 1): 0.6,
  (1, 1, 0): 0.6,
  (1, 1, 1): 0.4,
  (1, 2, 0): 0.7,
  (1, 2, 1): 0.3
}

def test_infer(t):
  return toy_A[t[0: 1]] * toy_B[t[0: 2]] * toy_C[t[0: 3]]

print(test_infer((0, 2, 1)))

def test_to_evidence(t):
  evidence = []
  evidence.append([(1, t[0])])
  evidence.append([(1, t[1] + 2)])
  # evidence.append([(1, t[2] + 5)])
  return evidence

def generate_assignments(weights):
  assignment = [ 0 for _ in range(len(weights)) ]
  in_range = True
  while in_range:
    assignment_weight = 1
    for i in range(len(weights)):
      if assignment[i] == 1:
        assignment_weight *= weights[i]
    yield tuple(assignment), assignment_weight
    in_range = False
    for i in range(len(weights) - 1, -1, -1):
      if assignment[i] == 0:
        assignment[i] += 1
        in_range = True
        break
      else:
        assignment[i] = 0

def check_sat(model, cnf):
  for clause in cnf:
    sat = False
    for lit in clause:
      if lit[0] == model[lit[1]]:
        sat = True
        break
    if not sat:
      return False
  return True

def count_models(weights, cnf):
  Z = 0
  energy = 0
  i = 0
  for assignment, weight in generate_assignments(weights):
    i += 1
    if i % 10000 == 0:
      print(i)
    Z += weight
    if check_sat(assignment, cnf):
      energy += weight
  return energy, Z

if __name__ == "__main__":
  graph_file = sys.argv[1]
  evidence_file = sys.argv[2]
  formula_file = sys.argv[3]
  weights_file = sys.argv[4]
  with open(graph_file) as gfile, open(evidence_file) as efile, open(formula_file, 'w') as ffile, open(weights_file, 'w') as wfile:
    graph = BayesGraph(gfile)
    graph.to_formula_file_with_evidence(efile, ffile, wfile)
    # weights, cnf = graph.to_formula()
    # f_weights = [ float(weight) for weight in weights ]
    
    # evidence = test_to_evidence((0, 2, 1))
    # energy, Z = count_models(f_weights, cnf)
    # print(energy, Z, energy / Z)