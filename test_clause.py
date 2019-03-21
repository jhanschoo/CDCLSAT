from __future__ import annotations
import unittest

from assignment import Assignment
from clause import Clause

class TestClause(unittest.TestCase):

  def test_init(self: TestClause):
    clause = Clause([-6, 5, -4, 3, -2, 1])
    self.assertEqual(clause.get_head_tail_var(), (6, 1))

  def test_assign(self: TestClause):
    clause = Clause([-6, 5, -4, 3, -2, 1])
    a1 = Assignment(set([1, 2, 3, 4, 5, 6]))
    a1.add_assignment(0, 6, 1, None)
    clause.assign(a1)
    self.assertEqual(clause.get_state(a1), (Clause.UNRESOLVED, 5, 1))
    self.assertEqual(clause.get_assigned_vars(a1), [6])
    a1.add_assignment(1, 5, 0, None)
    a1.add_assignment(2, 4, 1, None)
    a1.add_assignment(2, 1, 0, None)
    clause.assign(a1)
    self.assertEqual(clause.get_state(a1), (Clause.UNRESOLVED, 3, 2))
    self.assertEqual(clause.get_assigned_vars(a1), [6, 5, 4, 1])

  def test_valid_1(self: TestClause):
    clause = Clause([-6, 5, -4, 3, -2, 1])
    a1 = Assignment(set([1, 2, 3, 4, 5, 6]))
    a1.add_assignment(0, 6, 1, None)
    clause.assign(a1)
    a1.add_assignment(1, 5, 0, None)
    a1.add_assignment(2, 4, 1, None)
    a1.add_assignment(2, 1, 0, None)
    a1.add_assignment(2, 2, 0, None)
    clause.assign(a1)
    self.assertEqual(clause.get_state(a1), (Clause.SATISFIED, 3, 2))
    self.assertEqual(clause.get_assigned_vars(a1), [6, 5, 4, 2, 1])

  def test_valid_2(self: TestClause):
    clause = Clause([-6, 5, -4, 3, -2, 1])
    a1 = Assignment(set([1, 2, 3, 4, 5, 6]))
    a1.add_assignment(0, 6, 1, None)
    clause.assign(a1)
    a1.add_assignment(1, 5, 0, None)
    a1.add_assignment(2, 4, 1, None)
    a1.add_assignment(2, 1, 0, None)
    a1.add_assignment(2, 3, 0, None)
    a1.add_assignment(2, 2, 0, None)
    clause.assign(a1)
    self.assertEqual(clause.get_state(a1), (Clause.SATISFIED, 2, 2))
    self.assertEqual(clause.get_assigned_vars(a1), [6, 5, 4, 3, 2, 1])

  def test_unit(self: TestClause):
    clause = Clause([-6, 5, -4, 3, -2, 1])
    a1 = Assignment(set([1, 2, 3, 4, 5, 6]))
    a1.add_assignment(0, 6, 1, None)
    clause.assign(a1)
    a1.add_assignment(1, 5, 0, None)
    a1.add_assignment(2, 3, 0, None)
    a1.add_assignment(2, 4, 1, None)
    a1.add_assignment(2, 1, 0, None)
    clause.assign(a1)
    self.assertEqual(clause.get_state(a1), (Clause.UNIT, 2, 2))
    self.assertEqual(clause.get_assigned_vars(a1), [6, 5, 4, 3, 1])

  def test_unsat(self: TestClause):
    clause = Clause([-6, 5, -4, 3, -2, 1])
    a1 = Assignment(set([1, 2, 3, 4, 5, 6]))
    a1.add_assignment(0, 6, 1, None)
    clause.assign(a1)
    a1.add_assignment(1, 5, 0, None)
    a1.add_assignment(2, 3, 0, None)
    a1.add_assignment(2, 4, 1, None)
    a1.add_assignment(2, 1, 0, None)
    a1.add_assignment(2, 2, 1, None)
    clause.assign(a1)
    self.assertEqual(clause.get_state(a1), (Clause.UNSATISFIED, 1, 1))
    self.assertEqual(clause.get_assigned_vars(a1), [6, 5, 4, 3, 2, 1])

  def test_backtrack(self: TestClause):
    clause = Clause([-6, 5, -4, 3, -2, 1])
    a1 = Assignment(set([1, 2, 3, 4, 5, 6]))
    a1.add_assignment(0, 5, 0, None)
    a1.add_assignment(1, 3, 0, None)
    clause.assign(a1)
    a1.add_assignment(1, 6, 1, None)
    a1.add_assignment(1, 4, 1, None)
    a1.add_assignment(2, 1, 0, None)
    a1.add_assignment(2, 2, 1, None)
    clause.assign(a1)
    self.assertEqual(clause.get_state(a1), (Clause.UNSATISFIED, 1, 1))
    self.assertEqual(clause.get_assigned_vars(a1), [6, 5, 4, 3, 2, 1])
    clause.backtrack(1)
    a1.backtrack(1)
    self.assertEqual(clause.get_state(a1), (Clause.UNRESOLVED, 2, 1))
    self.assertEqual(clause.get_assigned_vars(a1), [6, 5, 4, 3])
    clause.backtrack(0)
    a1.backtrack(0)
    self.assertEqual(clause.get_state(a1), (Clause.UNRESOLVED, 6, 1))
    self.assertEqual(clause.get_assigned_vars(a1), [5])

if __name__ == "__main__":
  unittest.main()