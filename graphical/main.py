import sys

from bayes_graph import BayesGraph

if __name__ == "__main__":
  graph_file = sys.argv[1]
  evidence_file = sys.argv[2]
  formula_file = sys.argv[3]
  weights_file = sys.argv[4]
  with open(graph_file) as gfile, open(evidence_file) as efile, open(formula_file, 'w') as ffile, open(weights_file, 'w') as wfile:
    graph = BayesGraph(gfile)
    graph.to_formula_file_with_evidence(efile, ffile, wfile)