import os
import sys

import cdcl

if __name__ == "__main__":
  filename = sys.argv[1]
  with open(filename) as file:
    cdcl_satisfiable = cdcl.cdcl(file) == cdcl.SATISFIABLE
    if cdcl_satisfiable:
      print("SATISFIABLE")
    else:
      print("UNSATISFIABLE")