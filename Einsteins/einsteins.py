from __future__ import annotations
from typing import Dict, List

houses = sorted(["1", "2", "3", "4", "5"])
colors = sorted(["red", "white", "green", "yellow", "blue"])
nationalities = sorted(["Brit", "Swede", "Dane", "Norwegian", "German"])
pets = sorted(["dog", "bird", "cat", "horse", "fish"])
beverages = sorted(["tea", "coffee", "milk", "beer", "water"])
cigars = sorted(["PallMall", "Dunhill", "Blends", "Bluemasters", "Prince"])

def pigeonhole_constraints(prefix: str, subjs: List[str], objs: List[str]) -> List[List[str]]:
  formula = []
  # existence constraints
  for a in subjs:
    clause = []
    for b in objs:
      clause.append("{}.{}.{}".format(prefix, a, b))
    formula.append(clause)

  # exclusion constraints
  for a in subjs:
    for b1 in objs:
      for b2 in objs:
        if b1 >= b2:
          continue
        clause = [
          "-{}.{}.{}".format(prefix, a, b1),
          "-{}.{}.{}".format(prefix, a, b2)
        ]
        formula.append(clause)

  # existence constraints
  for b in objs:
    clause = []
    for a in subjs:
      clause.append("{}.{}.{}".format(prefix, a, b))
    formula.append(clause)

  # exclusion constraints
  for b in objs:
    for a1 in subjs:
      for a2 in subjs:
        if a1 >= a2:
          continue
        clause = [
          "-{}.{}.{}".format(prefix, a1, b),
          "-{}.{}.{}".format(prefix, a2, b)
        ]
        formula.append(clause)
  return formula

def equivalence_constraints(vars: List[str]):
  formula = []
  for conclusion in vars:
    clause = [conclusion]
    for predicate in vars:
      if predicate == conclusion:
        continue
      if predicate[0] == "-":
        clause.append(predicate[1:])
      else:
        clause.append("-" + predicate)
    formula.append(clause)
  return formula

formula = []
formula.extend(pigeonhole_constraints("Owns", nationalities, houses))
formula.extend(pigeonhole_constraints("HasColor", houses, colors))
formula.extend(pigeonhole_constraints("Rears", nationalities, pets))
formula.extend(pigeonhole_constraints("Drinks", nationalities, beverages))
formula.extend(pigeonhole_constraints("Smokes", nationalities, cigars))

# Neighbor constraints
for i in range(1, 4):
  for j in range(i+2, 6):
    formula.append(["-Neighbor.{}.{}".format(i, j)])
    formula.append(["-Neighbor.{}.{}".format(j, i)])
for i in range(1, 6):
  formula.append(["-Neighbor.{}.{}".format(i, i)])

# The Brit lives in the red house
for h in houses:
  formula.extend(equivalence_constraints(["Owns.Brit.{}".format(h), "HasColor.{}.red".format(h)]))

# The Swede keeps dogs as pets
formula.append(["Rears.Swede.dog"])

# The Dane drinks tea
formula.append(["Drinks.Dane.tea"])

# The green house is on the left of the white house
for i in range(1, 5):
  formula.extend(equivalence_constraints([
    "HasColor.{}.green".format(i),
    "HasColor.{}.white".format(i + 1)
  ]))
formula.append(["-HasColor.1.white"])
formula.append(["-HasColor.5.green"])

# The green house's owner drinks coffee
for n in nationalities:
  for h in houses:
    formula.extend(equivalence_constraints([
      "HasColor.{}.green".format(h),
      "Owns.{}.{}".format(n, h),
      "Drinks.{}.coffee".format(n)
    ]))

# The person who smokes Pall Mall rears birds
for n in nationalities:
  formula.extend(equivalence_constraints([
    "Rears.{}.bird".format(n),
    "Smokes.{}.PallMall".format(n)
  ]))

# The owner of the yellow house smokes Dunhill
for n in nationalities:
  for h in houses:
    formula.extend(equivalence_constraints([
      "HasColor.{}.yellow".format(h),
      "Owns.{}.{}".format(n, h),
      "Smokes.{}.Dunhill".format(n)
    ]))

# The man living in the center house drinks milk
for n in nationalities:
  formula.extend(equivalence_constraints([
    "Owns.{}.3".format(n),
    "Drinks.{}.milk".format(n)
  ]))

# The Norwegian lives in the first house
formula.append(["Owns.Norwegian.1"])

# The man who smokes Blends lives next to the one who keeps cats
for i in range(1, 6):
  for j in range(1, 6):
    for n1 in nationalities:
      for n2 in nationalities:
        formula.extend(equivalence_constraints([
        "Owns.{}.{}".format(n1, i),
        "Smokes.{}.Blends".format(n1),
        "Owns.{}.{}".format(n2, j),
        "Rears.{}.cat".format(n2, i),
        "Neighbor.{}.{}".format(i, j)
        ]))

# The man who keeps the horse lives next to the man who smokes Dunhill
for i in range(1, 6):
  for j in range(1, 6):
    for n1 in nationalities:
      for n2 in nationalities:
        formula.extend(equivalence_constraints([
          "Owns.{}.{}".format(n1, i),
          "Rears.{}.horse".format(n1),
          "Owns.{}.{}".format(n2, j),
          "Smokes.{}.Dunhill".format(n2),
          "Neighbor.{}.{}".format(i, j)
        ]))

# The owner who smokes Bluemasters drinks beer
for n in nationalities:
  formula.extend(equivalence_constraints([
    "Smokes.{}.Bluemasters".format(n),
    "Drinks.{}.beer".format(n)
  ]))

# The German smokes Prince
formula.append(["Smokes.German.Prince"])

# The Norwegian lives next to the blue house
for i in range(1, 6):
  for j in range(1, 6):
    formula.extend(equivalence_constraints([
      "Owns.Norwegian.{}".format(i),
      "HasColor.{}.blue".format(j),
      "Neighbor.{}.{}".format(i, j)
    ]))

# The man who smokes Blends has a neighbor who drinks water
for i in range(1, 6):
  for j in range(1, 6):
    for n1 in nationalities:
      for n2 in nationalities:
        formula.extend(equivalence_constraints([
          "Owns.{}.{}".format(n1,i),
          "Smokes.{}.Blends".format(n1),
          "Owns.{}.{}".format(n2,j),
          "Drinks.{}.water".format(n2),
          "Neighbors.{}.{}".format(i, j)
        ]))

for n in nationalities:
  with open("{}.cnf".format(n), "w") as file:
    evidenced_formula = list(formula)
    evidenced_formula.append(["Rears.{}.fish".format(n)])
    variables: List[str] = []
    variable_map: Dict[str, int] = {}
    cnf: List[List[int]] = []
    for clause in evidenced_formula:
      cnf_clause = []
      for lit in clause:
        sign = 1
        if lit[0] == "-":
          sign = -1
          lit = lit[1:]
        if lit not in variable_map:
          variable_map[lit] = len(variables) + 1
          variables.append(lit)
        cnf_clause.append(sign * variable_map[lit])
      cnf.append(cnf_clause)
    file.write("p cnf {} {} \n".format(len(variables), len(cnf)))
    for cnf_clause in cnf:
      file.write(" ".join((str(i) for i in cnf_clause)) + " 0\n")
