from __future__ import annotations
from typing import List, TextIO
import math
import os
import sys
import random

def random_formula(num_vars: int, num_clauses: int, lits_per_clause: int) -> List[List[int]]:
  return [ random_clause(num_vars, lits_per_clause) for _ in range(num_clauses) ]

def random_clause(num_vars: int, num_lits: int) -> List[int]:
  clause = random.sample(range(1, num_vars + 1), num_lits)
  for i in range(len(clause)):
    if random.randrange(2) == 0:
      clause[i] = -clause[i]
  return clause

def write_formula(file: TextIO, num_vars: int, formula: List[List[int]]) -> None:
  file.write("p cnf {} {}\n".format(num_vars, len(formula)))
  for clause in formula:
    lit_str = " ".join([str(l) for l in clause]) + " 0\n"
    file.write(lit_str)

def write_random_formula(filename: str, num_vars: int, num_clauses: int, lits_per_clause: int) -> None:
  with open(filename, "w") as file:
    formula = random_formula(num_vars, num_clauses, lits_per_clause)
    write_formula(file, num_vars, formula)

def gen_poly_3cnf_suite(path: str):
  MIN_NUM_CLAUSES = 32
  MAX_NUM_CLAUSES = 256
  STEP = 4
  INSTANCES = 16
  POW = 3
  K = 3
  for m in range(MIN_NUM_CLAUSES, MAX_NUM_CLAUSES + 1, STEP):
    for i in range(INSTANCES):
      n = math.ceil(m ** (1/POW))
      write_random_formula(
        os.path.join(path, "poly-{}-{}-{}.cnf".format(n, m, i)),
        n, m, K
      )

if __name__ == "__main__":
  gen_poly_3cnf_suite(sys.argv[1])