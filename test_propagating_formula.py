from __future__ import annotations
import io
import unittest

from propagating_formula import PropagatingFormula

PHI1C = io.StringIO(
"""c FILE:  phi1c.cnf
c
c SOURCE: Handbook of Satisfiability, by Joao Marques-Silva, Ines Lynce and Sharad Malik, 2008
p cnf 12 9
1 31 -2 0
1 -3 0
2 3 4 0
-4 -5 0
21 -4 -6 0
5 6 0
7 8 9 10 0
7 8 9 10 0
-10 0
""")

class TestPropagatingFormula(unittest.TestCase):
  def test_propagating_formula(self: TestPropagatingFormula):
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
    formula = PropagatingFormula(PHI1C)

    self.assertEqual(formula.get_current_decision_level(), 0)
    self.assertEqual(formula.get_current_state(), formula.UNRESOLVED)
    self.assertEqual(len(formula.formula.assignment), 1)
    formula.assign(8, 0)
    self.assertEqual(formula.get_current_decision_level(), 1)
    self.assertEqual(formula.get_current_state(), formula.UNRESOLVED)
    self.assertEqual(len(formula.formula.assignment), 2)
    formula.assign(21, 0)
    self.assertEqual(formula.get_current_decision_level(), 2)
    self.assertEqual(formula.get_current_state(), formula.UNRESOLVED)
    self.assertEqual(len(formula.formula.assignment), 3)
    formula.assign(31, 0)
    self.assertEqual(formula.get_current_decision_level(), 3)
    self.assertEqual(formula.get_current_state(), formula.UNRESOLVED)
    self.assertEqual(len(formula.formula.assignment), 4)
    formula.assign(7, 0)
    self.assertEqual(formula.get_current_decision_level(), 4)
    self.assertEqual(formula.get_current_state(), formula.UNRESOLVED)
    self.assertEqual(len(formula.formula.assignment), 6)
    formula.assign(1, 0)
    self.assertEqual(formula.get_current_decision_level(), 5)
    self.assertEqual(formula.get_current_state(), formula.UNSATISFIED)
    self.assertEqual(len(formula.formula.assignment), 12)
    formula.backtrack(4)
    self.assertEqual(formula.get_current_decision_level(), 4)
    self.assertEqual(formula.get_current_state(), formula.UNRESOLVED)
    self.assertEqual(len(formula.formula.assignment), 6)
    formula.backtrack(2)
    self.assertEqual(formula.get_current_decision_level(), 2)
    self.assertEqual(formula.get_current_state(), formula.UNRESOLVED)
    self.assertEqual(len(formula.formula.assignment), 3)
    formula.assign(31, 0)
    self.assertEqual(formula.get_current_decision_level(), 3)
    self.assertEqual(formula.get_current_state(), formula.UNRESOLVED)
    self.assertEqual(len(formula.formula.assignment), 4)
    formula.assign(7, 0)
    self.assertEqual(formula.get_current_decision_level(), 4)
    self.assertEqual(formula.get_current_state(), formula.UNRESOLVED)
    self.assertEqual(len(formula.formula.assignment), 6)
    formula.assign(1, 1)
    self.assertEqual(formula.get_current_decision_level(), 5)
    self.assertEqual(formula.get_current_state(), formula.UNRESOLVED)
    self.assertEqual(len(formula.formula.assignment), 7)
    formula.assign(5, 0)
    self.assertEqual(formula.get_current_decision_level(), 6)
    self.assertEqual(formula.get_current_state(), formula.UNRESOLVED)
    self.assertEqual(len(formula.formula.assignment), 10)
    formula.assign(2, 0)
    self.assertEqual(formula.get_current_decision_level(), 7)
    self.assertEqual(formula.get_current_state(), formula.SATISFIED)
    self.assertEqual(len(formula.formula.assignment), 12)