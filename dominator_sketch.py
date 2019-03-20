# https://www.cc.gatech.edu/~harrold/6340/cs6340_fall2009/Readings/lengauer91jul.pdf

from __future__ import annotations
from typing import Dict, List, Set, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
  Vertex = str

succ: Dict[Vertex, List[Vertex]] = {
  "R": ["C", "B", "A"],
  "C": ["F", "G"],
  "F": ["I"],
  "I": ["K"],
  "K": ["R", "I"],
  "G": ["I", "J"],
  "J": ["I"],
  "B": ["E", "A", "D"],
  "E": ["H"],
  "H": ["K", "E"],
  "A": ["D"],
  "D": ["L"],
  "L": ["H"]
}

# step 1

numbering: Dict[Vertex, int] = {}
vertex: Dict[int, Vertex] = {}
current_number = 0

parent: Dict[Vertex, Vertex] = {}

pred: Dict[Vertex, List[Vertex]] = {}

semi: Dict[Vertex, int] = {}
for v in succ:
  semi[v] = 0

def dfs(v: str):
  global current_number
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
    dfs(child)

dfs("R")

print("parent", parent)
print("pred", pred)
print("numbering", numbering)
print("semi", semi)

# step 2

forest_parent: Dict[str, str] = {}

def forest_link(v: str, w: str) -> None:
  forest_parent[w] = v

bucket: Dict[Vertex, Set[Vertex]] = {}

dom: Dict[Vertex, Vertex] = {}

def forest_eval(v: str):
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

for i in range(current_number, 1, -1):
  w = vertex[i]
  for v in pred[w]:
    u = forest_eval(v)
    if semi[u] < semi[w]:
      semi[w] = semi[u]
  bucket_key = vertex[semi[w]]
  if bucket_key not in bucket:
    bucket[bucket_key] = set()
  bucket[bucket_key].add(w)
  forest_link(parent[w], w)
  while bucket.get(parent[w]):
    v = bucket[parent[w]].pop()
    u = forest_eval(v)
    if semi[u] < semi[v]:
      dom[v] = u
    else:
      dom[v] = parent[w]

print("semi", { k: vertex[i] for (k, i) in semi.items() })

for i in range(2, current_number + 1):
  w = vertex[i]
  if dom[w] != vertex[semi[w]]:
    dom[w] = dom[dom[w]]

print("dom", dom)