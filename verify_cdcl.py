import os
import sys

import cdcl

if __name__ == "__main__":
  folder = sys.argv[1]
  counts = 0
  for filename in sorted(os.listdir(folder)):
    if filename[-4:] != ".cnf":
      continue
    with open(os.path.join(folder, filename)) as file:
      file.readline()[2:-1]
      sat_line = file.readline()[2:-1]
      #print(sat_line)
      satisfiable = sat_line == "SATISFIABLE"
      satisfiable_state, decision_counts = cdcl.cdcl(file)
      counts += decision_counts
      cdcl_satisfiable = satisfiable_state == cdcl.SATISFIABLE
      if cdcl_satisfiable != satisfiable:
        print("file {} is {} but cdcl reports otherwise".format(filename, sat_line))
  print("Decisions were made {} times".format(counts))