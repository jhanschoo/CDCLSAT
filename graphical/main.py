import sys

from bayes_graph import BayesGraph

if __name__ == "__main__":
  if len(sys.argv) != 5:
    print("Usage: python main.py path/to/graph_in.uai path/to/evidence_in.uai path/to/formula_out.cnf path/to/weights_out.weights")
    sys.exit(0)
  _, graph_file, evidence_file, formula_file, weights_file = sys.argv
  with open(graph_file) as gfile, open(evidence_file) as efile, open(formula_file, 'w') as ffile, open(weights_file, 'w') as wfile:
    graph = BayesGraph(gfile)
    graph.to_formula_file_with_evidence(efile, ffile, wfile)