from __future__ import annotations
import io
import unittest

from formula import Formula

PHIU = io.StringIO(
"""c FILE:  phi1u.cnf
c
p cnf 3 3
1 2 0
1 0
3 0
"""
)

PHI1C = io.StringIO(
"""c FILE:  phi1c.cnf
c
c SOURCE: Handbook of Satisfiability, by Joao Marques-Silva, Ines Lynce and Sharad Malik, 2008
p cnf 12 8
1 31 -2 0
1 -3 0
2 3 4 0
-4 -5 0
21 -4 -6 0
5 6 0
7 8 9 10 0
7 8 9 10 0
""")

class TestFormula(unittest.TestCase):
  def test_unit_clauses_on_input(self: TestFormula):
    formula = Formula(PHIU)
    self.assertEqual(formula.unit_clauses, set([formula.formula[1], formula.formula[2]]))

  def test_formula(self: TestFormula):
    """
    10 = 0 @ 0
    8 = 0 @ 1
    21 = 0 @ 2
    31 = 0 @ 3
    7 = 0 @ 4
    9 = 1 @ 4
    1 = 0 @ 5
    2 = 0 @ 5
    3 = 0 @ 5
    4 = 1 @ 5
    5 = 0 @ 5
    6 = 0 @ 5
    """
    formula = Formula(PHI1C)

    self.assertEqual(formula.base_state, Formula.UNRESOLVED)

    self.assertEqual(formula.variable_clauses, {
      1: set([
        formula.formula[1]
      ]),
      2: set([
        formula.formula[0],
        formula.formula[2]
      ]),
      3: set([
        formula.formula[1]
      ]),
      4: set([
        formula.formula[2],
        formula.formula[3]
      ]),
      5: set([
        formula.formula[3],
        formula.formula[5]
      ]),
      6: set([
        formula.formula[4],
        formula.formula[5]
      ]),
      7: set([
        formula.formula[6],
        formula.formula[7]
      ]),
      10: set([
        formula.formula[6],
        formula.formula[7]
      ]),
      21: set([
        formula.formula[4]
      ]),
      31: set([
        formula.formula[0]
      ]),
    })
    self.assertEqual(formula.mutation_history, [set()])
    self.assertEqual(formula.state_history, [Formula.UNRESOLVED])
    self.assertEqual(len(formula.assignment), 0)
    self.assertEqual(formula.unit_clauses, set())
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 0)

    formula.assign(0, 10, 0, None)
    self.assertEqual(formula.variable_clauses, {
      1: set([
        formula.formula[1]
      ]),
      2: set([
        formula.formula[0],
        formula.formula[2]
      ]),
      3: set([
        formula.formula[1]
      ]),
      4: set([
        formula.formula[2],
        formula.formula[3]
      ]),
      5: set([
        formula.formula[3],
        formula.formula[5]
      ]),
      6: set([
        formula.formula[4],
        formula.formula[5]
      ]),
      7: set([
        formula.formula[6],
        formula.formula[7]
      ]),
      9: set([
        formula.formula[6],
        formula.formula[7]
      ]),
      21: set([
        formula.formula[4]
      ]),
      31: set([
        formula.formula[0]
      ]),
    })
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ])
    ])
    self.assertEqual(formula.state_history, [Formula.UNRESOLVED])
    self.assertEqual(len(formula.assignment), 1)
    self.assertEqual(formula.unit_clauses, set())
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 0)
    
    formula.assign(1, 8, 0, None)
    self.assertEqual(formula.variable_clauses, {
      1: set([
        formula.formula[1]
      ]),
      2: set([
        formula.formula[0],
        formula.formula[2]
      ]),
      3: set([
        formula.formula[1]
      ]),
      4: set([
        formula.formula[2],
        formula.formula[3]
      ]),
      5: set([
        formula.formula[3],
        formula.formula[5]
      ]),
      6: set([
        formula.formula[4],
        formula.formula[5]
      ]),
      7: set([
        formula.formula[6],
        formula.formula[7]
      ]),
      9: set([
        formula.formula[6],
        formula.formula[7]
      ]),
      21: set([
        formula.formula[4]
      ]),
      31: set([
        formula.formula[0]
      ]),
    })
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ])
    ])
    self.assertEqual(formula.state_history, [Formula.UNRESOLVED, Formula.UNRESOLVED])
    self.assertEqual(len(formula.assignment), 2)
    self.assertEqual(formula.unit_clauses, set())
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 1)

    formula.assign(2, 21, 0, None)
    self.assertEqual(formula.variable_clauses, {
      1: set([
        formula.formula[1]
      ]),
      2: set([
        formula.formula[0],
        formula.formula[2]
      ]),
      3: set([
        formula.formula[1]
      ]),
      4: set([
        formula.formula[2],
        formula.formula[3],
        formula.formula[4]
      ]),
      5: set([
        formula.formula[3],
        formula.formula[5]
      ]),
      6: set([
        formula.formula[4],
        formula.formula[5]
      ]),
      7: set([
        formula.formula[6],
        formula.formula[7]
      ]),
      9: set([
        formula.formula[6],
        formula.formula[7]
      ]),
      31: set([
        formula.formula[0]
      ]),
    })
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set(),
      set([
        formula.formula[4]
      ])
    ])
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 3)
    self.assertEqual(formula.unit_clauses, set())
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 2)

    formula.assign(3, 31, 0, None)
    self.assertEqual(formula.variable_clauses, {
      1: set([
        formula.formula[1],
        formula.formula[0]
      ]),
      2: set([
        formula.formula[0],
        formula.formula[2]
      ]),
      3: set([
        formula.formula[1]
      ]),
      4: set([
        formula.formula[2],
        formula.formula[3],
        formula.formula[4]
      ]),
      5: set([
        formula.formula[3],
        formula.formula[5]
      ]),
      6: set([
        formula.formula[4],
        formula.formula[5]
      ]),
      7: set([
        formula.formula[6],
        formula.formula[7]
      ]),
      9: set([
        formula.formula[6],
        formula.formula[7]
      ]),
    })
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set(),
      set([
        formula.formula[4]
      ]),
      set([
        formula.formula[0]
      ])
    ])
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 4)
    self.assertEqual(formula.unit_clauses, set())
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 3)

    formula.assign(4, 7, 0, None)
    self.assertEqual(formula.variable_clauses, {
      1: set([
        formula.formula[1],
        formula.formula[0]
      ]),
      2: set([
        formula.formula[0],
        formula.formula[2]
      ]),
      3: set([
        formula.formula[1]
      ]),
      4: set([
        formula.formula[2],
        formula.formula[3],
        formula.formula[4]
      ]),
      5: set([
        formula.formula[3],
        formula.formula[5]
      ]),
      6: set([
        formula.formula[4],
        formula.formula[5]
      ]),
      9: set([
        formula.formula[6],
        formula.formula[7]
      ]),
    })
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set(),
      set([
        formula.formula[4]
      ]),
      set([
        formula.formula[0]
      ]),
      set([
        formula.formula[6],
        formula.formula[7]
      ])
    ])
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 5)
    self.assertEqual(formula.unit_clauses, set([
      formula.formula[6],
      formula.formula[7]
    ]))
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 4)

    formula.assign(4, 9, 1, None) # TODO: antecedent
    self.assertEqual(formula.variable_clauses, {
      1: set([
        formula.formula[1],
        formula.formula[0]
      ]),
      2: set([
        formula.formula[0],
        formula.formula[2]
      ]),
      3: set([
        formula.formula[1]
      ]),
      4: set([
        formula.formula[2],
        formula.formula[3],
        formula.formula[4]
      ]),
      5: set([
        formula.formula[3],
        formula.formula[5]
      ]),
      6: set([
        formula.formula[4],
        formula.formula[5]
      ]),
    })
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set(),
      set([
        formula.formula[4]
      ]),
      set([
        formula.formula[0]
      ]),
      set([
        formula.formula[6],
        formula.formula[7]
      ])
    ])
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 6)
    self.assertEqual(formula.unit_clauses, set())
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 4)

    formula.assign(5, 1, 0, None)
    self.assertEqual(formula.variable_clauses, {
      2: set([
        formula.formula[0],
        formula.formula[2]
      ]),
      3: set([
        formula.formula[1]
      ]),
      4: set([
        formula.formula[2],
        formula.formula[3],
        formula.formula[4]
      ]),
      5: set([
        formula.formula[3],
        formula.formula[5]
      ]),
      6: set([
        formula.formula[4],
        formula.formula[5]
      ]),
    })
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set(),
      set([
        formula.formula[4]
      ]),
      set([
        formula.formula[0]
      ]),
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set([
        formula.formula[1],
        formula.formula[0]
      ])
    ])
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 7)
    self.assertEqual(formula.unit_clauses, set([
      formula.formula[0],
      formula.formula[1]
    ]))
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 5)

    formula.assign(5, 2, 0, None) # TODO: antecedent
    self.assertEqual(formula.variable_clauses, {
      3: set([
        formula.formula[1],
        formula.formula[2]
      ]),
      4: set([
        formula.formula[2],
        formula.formula[3],
        formula.formula[4]
      ]),
      5: set([
        formula.formula[3],
        formula.formula[5]
      ]),
      6: set([
        formula.formula[4],
        formula.formula[5]
      ]),
    })
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set(),
      set([
        formula.formula[4]
      ]),
      set([
        formula.formula[0]
      ]),
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set([
        formula.formula[1],
        formula.formula[0],
        formula.formula[2]
      ])
    ])
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 8)
    self.assertEqual(formula.unit_clauses, set([
      formula.formula[1]
    ]))
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 5)

    formula.assign(5, 3, 0, None) # TODO: antecedent
    self.assertEqual(formula.variable_clauses, {
      4: set([
        formula.formula[2],
        formula.formula[3],
        formula.formula[4]
      ]),
      5: set([
        formula.formula[3],
        formula.formula[5]
      ]),
      6: set([
        formula.formula[4],
        formula.formula[5]
      ]),
    })
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set(),
      set([
        formula.formula[4]
      ]),
      set([
        formula.formula[0]
      ]),
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set([
        formula.formula[1],
        formula.formula[0],
        formula.formula[2]
      ])
    ])
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 9)
    self.assertEqual(formula.unit_clauses, set([
      formula.formula[2]
    ]))
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 5)

    formula.assign(5, 4, 1, None) # TODO: antecedent
    self.assertEqual(formula.variable_clauses, {
      5: set([
        formula.formula[3],
        formula.formula[5]
      ]),
      6: set([
        formula.formula[4],
        formula.formula[5]
      ]),
    })
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set(),
      set([
        formula.formula[4]
      ]),
      set([
        formula.formula[0]
      ]),
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set([
        formula.formula[1],
        formula.formula[0],
        formula.formula[2],
        formula.formula[3],
        formula.formula[4]
      ])
    ])
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 10)
    self.assertEqual(formula.unit_clauses, set([
      formula.formula[3],
      formula.formula[4]
    ]))
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 5)

    formula.assign(5, 5, 0, None) # TODO: antecedent
    self.assertEqual(formula.variable_clauses, {
      6: set([
        formula.formula[4],
        formula.formula[5]
      ]),
    })
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set(),
      set([
        formula.formula[4]
      ]),
      set([
        formula.formula[0]
      ]),
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set([
        formula.formula[1],
        formula.formula[0],
        formula.formula[2],
        formula.formula[3],
        formula.formula[4],
        formula.formula[5]
      ])
    ])
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 11)
    self.assertEqual(formula.unit_clauses, set([
      formula.formula[4],
      formula.formula[5]
    ]))
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 5)

    formula.assign(5, 6, 0, None) # TODO: antecedent
    self.assertEqual(formula.variable_clauses, {})
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set(),
      set([
        formula.formula[4]
      ]),
      set([
        formula.formula[0]
      ]),
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set([
        formula.formula[1],
        formula.formula[0],
        formula.formula[2],
        formula.formula[3],
        formula.formula[4],
        formula.formula[5]
      ])
    ])
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNSATISFIED
    ])
    self.assertEqual(len(formula.assignment), 12)
    self.assertEqual(formula.unit_clauses, set())
    self.assertEqual(formula.unsat_clauses, set([
      formula.formula[5]
    ]))
    self.assertEqual(formula.decision_level, 5)

    formula.backtrack(4)
    self.assertEqual(formula.variable_clauses, {
      1: set([
        formula.formula[1],
        formula.formula[0]
      ]),
      2: set([
        formula.formula[0],
        formula.formula[2]
      ]),
      3: set([
        formula.formula[1]
      ]),
      4: set([
        formula.formula[2],
        formula.formula[3],
        formula.formula[4]
      ]),
      5: set([
        formula.formula[3],
        formula.formula[5]
      ]),
      6: set([
        formula.formula[4],
        formula.formula[5]
      ]),
    })
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set(),
      set([
        formula.formula[4]
      ]),
      set([
        formula.formula[0]
      ]),
      set([
        formula.formula[6],
        formula.formula[7]
      ])
    ])
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 6)
    self.assertEqual(formula.unit_clauses, set())
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 4)

    formula.backtrack(2)
    self.assertEqual(formula.variable_clauses, {
      1: set([
        formula.formula[1]
      ]),
      2: set([
        formula.formula[0],
        formula.formula[2]
      ]),
      3: set([
        formula.formula[1]
      ]),
      4: set([
        formula.formula[2],
        formula.formula[3],
        formula.formula[4]
      ]),
      5: set([
        formula.formula[3],
        formula.formula[5]
      ]),
      6: set([
        formula.formula[4],
        formula.formula[5]
      ]),
      7: set([
        formula.formula[6],
        formula.formula[7]
      ]),
      9: set([
        formula.formula[6],
        formula.formula[7]
      ]),
      31: set([
        formula.formula[0]
      ]),
    })
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set(),
      set([
        formula.formula[4]
      ])
    ])
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 3)
    self.assertEqual(formula.unit_clauses, set())
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 2)

    formula.assign(3, 31, 0, None)
    self.assertEqual(formula.mutation_history, [
      set([
        formula.formula[6],
        formula.formula[7]
      ]),
      set(),
      set([
        formula.formula[4]
      ]),
      set([
        formula.formula[0]
      ])
    ])
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 4)
    self.assertEqual(formula.unit_clauses, set())
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 3)

    formula.assign(4, 7, 0, None)
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 5)
    self.assertEqual(formula.unit_clauses, set([
      formula.formula[6],
      formula.formula[7]
    ]))
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 4)

    formula.assign(4, 9, 1, None)
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 6)
    self.assertEqual(formula.unit_clauses, set())
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 4)

    formula.assign(5, 1, 1, None)
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 7)
    self.assertEqual(formula.unit_clauses, set())
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 5)

    formula.assign(6, 5, 0, None)
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 8)
    self.assertEqual(formula.unit_clauses, set([
      formula.formula[5]
    ]))
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 6)

    formula.assign(6, 6, 1, None)
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 9)
    self.assertEqual(formula.unit_clauses, set([
      formula.formula[4]
    ]))
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 6)

    formula.assign(6, 4, 0, None)
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 10)
    self.assertEqual(formula.unit_clauses, set())
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 6)

    formula.assign(7, 2, 0, None)
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED
    ])
    self.assertEqual(len(formula.assignment), 11)
    self.assertEqual(formula.unit_clauses, set([
      formula.formula[2]
    ]))
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 7)

    formula.assign(7, 3, 1, None)
    self.assertEqual(formula.state_history, [
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.UNRESOLVED,
      Formula.SATISFIED
    ])
    self.assertEqual(len(formula.assignment), 12)
    self.assertEqual(formula.unit_clauses, set())
    self.assertEqual(formula.unsat_clauses, set())
    self.assertEqual(formula.decision_level, 7)