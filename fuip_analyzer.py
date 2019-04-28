from __future__ import annotations
from typing import Dict, List, Optional, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
  from shared_types import DecisionLevel, Literal

  from assignment import Assignment, AssignmentItem
  from clause import Clause
  from propagating_formula import PropagatingFormula

  Vertex = AssignmentItem

KAPPA: AssignmentItem = (-1, 0, 0.5, None)

def _build_conflict_dag(d: DecisionLevel, unsat_clauses: Set[Clause], assignment: Assignment) -> Tuple[AssignmentItem, Dict[AssignmentItem, Set[AssignmentItem]]]:
  succ: Dict[AssignmentItem, Set[AssignmentItem]] = {
    KAPPA: set()
  }
  queue: Set[AssignmentItem] = set()
  seen: Set[AssignmentItem] = set()
  root: Optional[AssignmentItem] = None
  for clause in unsat_clauses:
    for var in clause.get_assigned_vars(assignment):
      var_item = assignment.get(var)
      if not var_item:
        raise Exception("variable {} should be present in assignment".format(var))
      if var_item not in succ:
        succ[var_item] = set()
      succ[var_item].add(KAPPA)
      queue.add(var_item)
  while queue:
    var_item = queue.pop()
    if var_item in seen:
      continue
    seen.add(var_item)
    antecedent = var_item[3]
    if var_item[0] != d or not antecedent:
      if var_item[0] == d:
        root = var_item
      continue
    antecedent_vars = antecedent.get_assigned_vars(assignment)
    for v in antecedent_vars:
      if v == var_item[1]:
        continue
      parent_var_item = assignment.get(v)
      if not parent_var_item:
        raise Exception("variable {} should be present in assignment".format(v))
      if parent_var_item not in succ:
        succ[parent_var_item] = set()
      succ[parent_var_item].add(var_item)
      queue.add(parent_var_item)
  if not root:
    raise Exception("root should be found when building conflict tree")
  return root, succ

def _build_pred(succ: Dict[Vertex, Set[Vertex]]) -> Dict[Vertex, Set[Vertex]]:
  pred: Dict[Vertex, Set[Vertex]] = {}
  for p, cs in succ.items():
    for c in cs:
      if c not in pred:
        pred[c] = set()
      pred[c].add(p)
  return pred

def _forest_link(v: Vertex, w: Vertex, forest_parent: Dict[Vertex, Vertex]) -> None:
  forest_parent[w] = v

def _forest_eval(v: Vertex, forest_parent: Dict[Vertex, Vertex], semi: Dict[Vertex, int]) -> Vertex:
  if v not in forest_parent:
    return v
  u = v
  semi_u = semi[u]
  while forest_parent[v] in forest_parent:
    v = forest_parent[v]
    if semi[v] < semi_u:
      u = v
      semi_u = semi[u]
  return u

def _build_dominator_graph(root: Vertex, succ: Dict[AssignmentItem, Set[AssignmentItem]]) -> Dict[Vertex, Vertex]:
  dfs_stack: List[Vertex] = [root]

  # Step 1
  numbering: Dict[Vertex, int] = {}
  vertex: Dict[int, Vertex] = {}
  current_number = 0

  parent: Dict[Vertex, Vertex] = {}

  pred: Dict[Vertex, List[Vertex]] = {}

  semi: Dict[Vertex, int] = {}
  for v in succ:
    semi[v] = 0

  while dfs_stack:
    v = dfs_stack.pop()
    current_number += 1
    numbering[v] = current_number
    semi[v] = current_number
    vertex[current_number] = v
    children = succ[v]
    # initialize for steps 2, 3, 4
    for child in children:
      if child not in pred:
        pred[child] = []
      pred[child].append(v)
      if child in numbering:
        continue
      parent[child] = v
      dfs_stack.append(child)

  # step 2, with step 3 nested

  forest_parent: Dict[Vertex, Vertex] = {}

  bucket: Dict[Vertex, Set[Vertex]] = {}

  dom: Dict[Vertex, Vertex] = {}

  for i in range(current_number, 1, -1):
    w = vertex[i]
    for v in pred[w]:
      u = _forest_eval(v, forest_parent, semi)
      if semi[u] < semi[w]:
        semi[w] = semi[u]
    bucket_key = vertex[semi[w]]
    if bucket_key not in bucket:
      bucket[bucket_key] = set()
    bucket[bucket_key].add(w)
    _forest_link(parent[w], w, forest_parent)
    while bucket.get(parent[w]):
      v = bucket[parent[w]].pop()
      u = _forest_eval(v, forest_parent, semi)
      if semi[u] < semi[v]:
        dom[v] = u
      else:
        dom[v] = parent[w]
  return dom

def _build_clause(fuip: AssignmentItem, pred: Dict[AssignmentItem, Set[AssignmentItem]]) -> Tuple[DecisionLevel, List[Literal]]:
  stack: List[AssignmentItem] = [KAPPA]
  seen: Set[AssignmentItem] = set()
  conflicting_vars: Set[AssignmentItem] = set()
  d = fuip[0]
  max_sub_d: int = 0
  while stack:
    v = stack.pop()
    if v in seen:
      continue
    seen.add(v)
    if v == fuip or (v != KAPPA and v[0] != d):
      if (v != KAPPA and v[0] != d) and max_sub_d < v[0]:
        max_sub_d = v[0]
      conflicting_vars.add(v)
      continue
    for p in pred[v]:
      stack.append(p)
  clause = [
    (-var if val == 1 else var) for _, var, val, _ in conflicting_vars
  ]
  if d == 0:
    max_sub_d = -1
  return max_sub_d, clause

def fuip_analyzer(formula: PropagatingFormula) -> Tuple[DecisionLevel, List[List[Literal]]]:
  root, succ = _build_conflict_dag(formula.get_decision_level(), formula.get_unsat_clauses(), formula.get_partial_assignment())
  dom = _build_dominator_graph(root, succ)
  fuip = dom[KAPPA]
  pred = _build_pred(succ)
  backtrack_d, clause = _build_clause(fuip, pred)
  return backtrack_d, [clause]