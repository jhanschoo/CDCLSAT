from __future__ import annotations
from typing import List

houses = sorted(["1", "2", "3", "4", "5"])
colors = sorted(["red", "white", "green", "yellow", "blue"])
nationalities = sorted(["Brit", "Swede", "Dane", "Norwegian", "German"])
pets = sorted(["dog", "bird", "cat", "horse", "fish"])
beverages = sorted(["tea", "coffee", "milk", "beer", "water"])
cigars = sorted(["PallMall", "Dunhill", "Blends", "Bluemasters", "Prince"])

def bijection_constraints(prefix: str, subjs: List[str], objs: List[str]) -> List[List[str]]:
  formula = []
  # existence constraints
  for a in subjs:
    clause = []
    for b in objs:
      clause.append("{}.{}.{}".format(prefix, a, b))
    formula.append(clause)

  # exclusion constraints
  for a in subjs:
    for b1 in subjs:
      for b2 in subjs:
        if b1 >= b2:
          continue
        clause = [
          "-{}.{}.{}".format(prefix, a, b1),
          "-{}.{}.{}".format(prefix, a, b2)
        ]
        formula.append(clause)
  return formula

formula = []
formula.extend(bijection_constraints("Owns", nationalities, houses))
formula.extend(bijection_constraints("HasColor", houses, colors))
formula.extend(bijection_constraints("Rears", nationalities, pets))
formula.extend(bijection_constraints("Drinks", nationalities, beverages))
formula.extend(bijection_constraints("Smokes", nationalities, cigars))

# The Brit lives in the red house
for h in houses:
  formula.append(["-Owns.Brit.{}".format(h), "HasColor.{}.red".format(h)])

# The Swede keeps dogs as pets
formula.append(["Rears.Swede.dog"])

# The Dane drinks tea
formula.append(["Drinks.Dane.tea"])

# The green house is on the left of the white house
for i in range(1, 5):
  formula.append([
    "-HasColor.{}.green".format(i),
    "HasColor.{}.white".format(i + 1)
  ])

# The green house's owner drinks coffee
for n in nationalities:
  for h in houses:
    formula.append([
      "-HasColor.{}.green".format(h),
      "-Owns.{}.{}".format(n, h),
      "Drinks.{}.coffee".format(n)
    ])

# The person who smokes Pall Mall rears birds
for n in nationalities:
  formula.append([
    "-Rears.{}.bird".format(n),
    "Smokes.{}.PallMall".format(n)
  ])

# The owner of the yellow house smokes Dunhill
for n in nationalities:
  for h in houses:
    formula.append([
      "-HasColor.{}.yellow".format(h),
      "-Owns.{}.{}".format(n, h),
      "Smokes.{}.Dunhill".format(n)
    ])

# The man living in the center house drinks milk
for n in nationalities:
  formula.append([
    "-Owns.{}.3".format(n),
    "Drinks.{}.milk".format(n)
  ])

# The Norwegian lives in the first house
formula.append(["Owns.Norwegian.1"])

# The man who smokes Blends lives next to the one who keeps cats
for i in range(1, 6):
  for n1 in nationalities:
    for n2 in nationalities:
      formula.append([
        "-Owns.{}.{}".format(n1, i),
        "-Smokes.{}.Blends".format(n1),
      ])